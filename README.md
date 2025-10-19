# DocuMind - Setup & Usage

## 1. Install dependencies

```sh
pip install -r requirements.txt
```


## 2. Environment Variables

Copy `.env.example` to `.env` in the project root and fill in your secrets and connection details:

```sh
cp .env.example .env
```


## 3. Index your documents

```sh
python -m core.indexing
```

## 4. Start the API server (retrieval)

```sh
uvicorn api.main:app --reload
```

## 5. Start the worker

```sh
python -m worker.main
```

## 6. Launch the Streamlit UI

```sh
pip install streamlit
streamlit run ui/app.py
```

The UI will be available at http://localhost:8501 by default.

---
Ensure MongoDB, Redis, and Qdrant are running and accessible as configured in your `.env` file.
# RAG-based Document Analyser Agent

A Retrieval-Augmented Generation (RAG) agent that answers questions using content retrieved from PDF files.  
The assistant only uses the provided context (`page_contents` + `page_number`) and always points to the correct page for reference.

## Features
- Extracts and indexes PDF content for retrieval.
- Answers only from retrieved context (no hallucinations).
- Provides page references for navigation.

## Usage
1. Add your PDF file(s) to the `documents/` folder.
2. Run the pipeline to build the vector index.
3. Ask questions about the PDF
