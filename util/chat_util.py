import os
from config import config
from chromadb import HttpClient
from chromadb.utils import embedding_functions
from langchain.globals import set_debug
from langchain_core.embeddings import Embeddings
from chromadb.api.types import EmbeddingFunction
from langchain_community.llms import LlamaCpp
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.chains import create_retrieval_chain, create_history_aware_retriever

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env'))

set_debug(bool(os.getenv('LANGCHAIN_DEBUG')))


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
        <|user|>
        Given a chat history and the latest user question which might reference context in the chat history, 
        formulate a standalone question which can be understood without the chat history. Do NOT answer 
        the question, just reformulate it if needed and otherwise return it as is.
        <|end|>
    """
    user_input_prompt = """
        <|user|>
        As an expert political analyst on the US electoral process:
        1. Answer questions with certainty based on your knowledge and the provided context.
        2. Do not hallucinate or invent information.
        3. If unsure, politely state that you lack sufficient knowledge to answer.
        4. Generate new content by analyzing the supplied context. Avoid adding 'Based on the provided context' in your responses
        5. Use your previous knowledge when appropriate or when the context is insufficient.
        6. For simple greetings, respond appropriately without analysis.

        Context:
        {context}

        Question: {input}
        <|end|>
    """

    model = LlamaCpp(
        model_path="./Phi-3-mini-4k-instruct-q4.gguf",  # path to GGUF file
        n_ctx=4096,  # The max sequence length to use - note that longer sequence lengths require much more resources
        n_threads=4,
        stop=["<|end|>"]
    )

    rag_llm = None

    @classmethod
    def init_llm(cls):
        if not cls.rag_llm:
            # get chromadb retriever from vector store
            retriever = cls.vector_store.as_retriever(search_kwargs={"k": 3})

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
        return RedisChatMessageHistory(session_id, url=f"{config.REDIS_CONNECTION_STRING}")
