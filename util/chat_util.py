import torch
from config import config
from chromadb import HttpClient
from transformers import pipeline
from langchain.vectorstores import Chroma

from langchain.llms import HuggingFacePipeline
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
from langchain.chains import create_retrieval_chain, create_history_aware_retriever


class LLMUtil:

    model_name = config.MODEL_NAME
    vector_store = Chroma(client=HttpClient(),
                          embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
                          collection_name=config.COLLECTION_NAME)
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
        context supplied with each user question. Using this knowledge, answer the following questions.
        Here is the context to help:
        
        {context}
        
        [/INST]
    """
    rag_llm = None

    @classmethod
    def init_llm(cls):
        if not cls.rag_llm:
            # init tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
            tokenizer.padding_side = 'right'
            tokenizer.pad_token = tokenizer.eos_token

            # bits and bytes quantization configuration
            bnb_compute_dtype = getattr(torch, 'float16')
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=bnb_compute_dtype,
                bnb_4bit_use_double_quant=False,
            )

            # Quantize Model
            model = AutoModelForCausalLM.from_pretrained(
                config.MODEL_NAME,
                quantization_config=quantization_config,
            )

            # initialize a huggingface pipeline
            text_generation_pipeline = pipeline(
                model=model,
                tokenizer=tokenizer,
                task='text-generation',
                temperature=0.2,
                repetition_penalty=1.1,
                return_full_text=True,
                max_new_tokens=1000
            )

            # init langchain llm using huggingface pipeline
            llm_pipeline = HuggingFacePipeline(pipeline=text_generation_pipeline)

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
                llm_pipeline,
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
            question_answer_chain = create_stuff_documents_chain(llm_pipeline, chat_prompt)

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
        return RedisChatMessageHistory(session_id, url=config.REDIS_BROKER_URL)
