from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
import os
current_dir=os.path.dirname(__file__)
print(current_dir)
pdf_path=os.path.join(current_dir,"ThaiRecipes.pdf")
loader=PyPDFLoader(pdf_path)
docs=loader.load()
embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=50)
docs_split=text_splitter.split_documents(docs)
vector_store=FAISS.from_documents(docs_split,embedding)
retriever=vector_store.as_retriever()
retriever_tool=create_retriever_tool(
    retriever,
    "retrieve_recipe_book",
    "Search and return information about thai recipe",
)