

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from config.settings import settings

def get_embeddings():
    return AzureOpenAIEmbeddings(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        model=settings.AZURE_OPENAI_DEPLOYMENT
    )

def index_documents():
    documents_dir = settings.DOCUMENTS_DIR
    pdf_files = list(documents_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")

    embeddings = get_embeddings()

    for pdf_path in pdf_files:
        print(f"Loading {pdf_path}")
        loader = PyPDFLoader(file_path=pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} docs from {pdf_path}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=500,
            separators=[
                "\n\n", "\n", " ", ".", ",", "\u200b", "\uff0c", "\u3001", "\uff0e", "\u3002", ""
            ],
        )
        chunks = text_splitter.split_documents(documents=docs)
        print(f"Split into {len(chunks)} chunks.")

        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=settings.QDRANT_URL,
            collection_name=settings.QDRANT_COLLECTION
        )

    print("Indexing of Documents Done...")

if __name__ == "__main__":
    index_documents()
