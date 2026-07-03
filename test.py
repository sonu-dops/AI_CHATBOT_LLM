import os
import streamlit as st
from dotenv import load_dotenv

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Gemini RAG Assistant", page_icon="📚")
st.title("📚 RAG PDF Assistant")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. PDF Processing
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file and "vector_store" not in st.session_state:
    with st.spinner("Indexing document..."):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        loader = PyPDFLoader("temp.pdf")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        st.session_state.vector_store = FAISS.from_documents(splits, embeddings)
        st.success("Document indexed!")

# 3. Chat Logic
if prompt := st.chat_input("Ask a question about your PDF:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "vector_store" in st.session_state:
        with st.chat_message("assistant"):
            # Initialize LLM
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
            
            # Setup Prompt
            prompt_template = ChatPromptTemplate.from_template("""
                Answer the question based only on the following context:
                {context}
                
                Question: {input}
            """)
            
            # Create Chains
            combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)
            retrieval_chain = create_retrieval_chain(st.session_state.vector_store.as_retriever(), combine_docs_chain)
            
            # Invoke
            response = retrieval_chain.invoke({"input": prompt})
            answer = response["answer"]
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.warning("Please upload a document first.")