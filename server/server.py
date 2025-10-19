from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from pymongo import MongoClient
import redis
from rq import Queue
import worker

app = FastAPI()

# Setup Redis connection for RQ (valkey)
redis_conn = redis.Redis(host='valkey', port=6379, db=0)
queue = Queue('rag-queries', connection=redis_conn)

# Setup MongoDB connection
mongo_client = MongoClient('mongodb://admin:admin@mongodb:27017/')
db = mongo_client['rag_jobs']
collection = db['job_status']

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    job_id = str(uuid4())
    # Insert job status as 'queued'
    collection.insert_one({'job_id': job_id, 'status': 'queued', 'query': request.query})
    # Enqueue job to RQ
    queue.enqueue(worker.process_query, job_id, request.query)
    return {"job_id": job_id, "status": "queued"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = collection.find_one({'job_id': job_id})
    if not job:
        return {"error": "Job not found"}
    return {"job_id": job_id, "status": job.get('status'), "answer": job.get('answer'), "error": job.get('error')}

@app.get("/")
async def root():
    return {"message": "DocuMind FastAPI server is running."}
