import os
import numpy as np
from config import config
from chromadb import HttpClient
from langchain.vectorstores import Chroma
from chromadb.utils import embedding_functions
from langchain_core.embeddings import Embeddings
from chromadb.api.types import EmbeddingFunction
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
from langchain.chains import create_retrieval_chain, create_history_aware_retriever

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))


class ChromaEmbeddingsAdapter(Embeddings):
    def __init__(self, ef: EmbeddingFunction):
        self.ef = ef

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, query):
        return self.ef([query])[0]


class LLMUtil:

    embedding_fn = ChromaEmbeddingsAdapter(
        embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2"))

    vector_store = Chroma(client=HttpClient(os.getenv('CHROMA_DB_URL')),
                          collection_name=os.getenv('DB_NAME'),
                          embedding_function=embedding_fn)

    chat_history_prompt = """
        Given a chat history and the latest user question which might reference context in the chat history, 
        formulate a standalone question which can be understood without the chat history. Do NOT answer 
        the question, just reformulate it if needed and otherwise return it as is.
    """
    user_input_prompt = """
        ### [INST]
        Instruction: You are an expert political analyst with vast knowledge of the United States electoral process.
        You answer questions with certainty and you do not hallucinate. When unsure, you politely reply that you do 
        not have sufficient knowledge to answer the user question. You will generate new content by analysing the 
        context supplied with each user question. When your previous knowledge is capable of answering the questions, 
        or when the supplied context isn't enough to do so, you can default to previous knowledge. Using these 
        instructions, answer the following questions. Here is the supplied context:
        
        {context}
        
        [/INST]
    """

    model = ChatMistralAI(mistral_api_key=os.getenv('MISTRAL_API_KEY'))

    rag_llm = None

    @classmethod
    def init_llm(cls):
        if not cls.rag_llm:
            # get chromadb retriever from vector store
            retriever = cls.vector_store.as_retriever()

            # create template for user history prompt
            chat_history_context_prompt = ChatPromptTemplate.from_messages(
                [('system', cls.chat_history_prompt),
                 MessagesPlaceholder('chat_history'),
                 ('human', '{input}'),
                 ]
            )

            # create history aware retriever using chromadb retriever
            history_aware_retriever = create_history_aware_retriever(
                cls.model,
                retriever,
                chat_history_context_prompt
            )

            # New question/answer prompt
            chat_prompt = ChatPromptTemplate.from_messages(
                [('system', cls.user_input_prompt),
                 MessagesPlaceholder('chat_history'),
                 ('human', '{input}')
                 ]
            )

            # create document chain
            question_answer_chain = create_stuff_documents_chain(cls.model, chat_prompt)

            # create rag_chain using system and user prompts
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

            # create runnable llm with message history
            rag_chain_llm = RunnableWithMessageHistory(
                rag_chain,
                cls.get_message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

            cls.rag_llm = rag_chain_llm

        return cls.rag_llm

    @staticmethod
    def get_message_history(session_id: str) -> RedisChatMessageHistory:
        return RedisChatMessageHistory(session_id, url=f"{config.REDIS_BROKER_URL}/2")
