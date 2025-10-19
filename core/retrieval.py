

from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import AzureOpenAI
from config.settings import settings

def get_embeddings():
    return AzureOpenAIEmbeddings(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        model=settings.AZURE_OPENAI_DEPLOYMENT
    )

def get_vector_db(embeddings):
    return QdrantVectorStore.from_existing_collection(
        url=settings.QDRANT_URL,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embeddings,
    )

def get_azure_client():
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION
    )

import os

def load_system_prompt(context: str) -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/system_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        template = f.read()
    return template.replace('{context}', context)

def format_context_chunks(search_results):
    # Format context as a JSON-like list of dicts for the LLM (with content)
    context_chunks = []
    for doc in search_results:
        context_chunks.append({
            "page_number": doc.metadata.get('page_label', ''),
            "content": doc.page_content,
            "source": doc.metadata.get('source', '')
        })
    return context_chunks

def retrieve_answer(user_query: str) -> dict:
    """
    Retrieve relevant context from Qdrant and get LLM answer for the user query.
    Returns a dict with keys: answer, references (list of dicts with page_number, content, source)
    """
    embeddings = get_embeddings()
    vector_db = get_vector_db(embeddings)
    client = get_azure_client()

    search_results = vector_db.similarity_search(query=user_query)
    context_chunks = format_context_chunks(search_results)


    # For the LLM, provide a stringified version of the context chunks (with content)
    context_str = '\n'.join([
        f"Page: {chunk['page_number']}\nContent: {chunk['content']}\nSource: {chunk['source']}"
        for chunk in context_chunks
    ])
    system_prompt = load_system_prompt(context_str)

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
    )

    # The LLM is instructed to return a JSON string, so parse it
    import json
    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        # If parsing fails, return the raw output for debugging (with content in references)
        return {"answer": response.choices[0].message.content, "references": context_chunks}
