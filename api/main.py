
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from pymongo import MongoClient
import redis
from rq import Queue
from worker.main import process_query
from config.settings import settings

app = FastAPI()

# Setup Redis connection for RQ (valkey)
redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
queue = Queue('rag-queries', connection=redis_conn)

# Setup MongoDB connection
mongo_client = MongoClient(settings.MONGODB_URI)
db = mongo_client[settings.MONGODB_DB]
collection = db[settings.MONGODB_COLLECTION]

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    job_id = str(uuid4())
    # Insert job status as 'queued'
    collection.insert_one({'job_id': job_id, 'status': 'queued', 'query': request.query})
    # Enqueue job to RQ
    queue.enqueue(process_query, job_id, request.query)
    return {"job_id": job_id, "status": "queued"}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = collection.find_one({'job_id': job_id})
    if not job:
        return {"error": "Job not found"}
    return {
        "job_id": job_id,
        "status": job.get('status'),
        "answer": job.get('answer'),
        "references": job.get('references'),
        "error": job.get('error')
    }

@app.get("/")
async def root():
    return {"message": "DocuMind FastAPI server is running."}