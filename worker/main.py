
from rq import Worker, Queue
from rq.connections import Connection
from pymongo import MongoClient
from core.retrieval import retrieve_answer
import redis
from config.settings import settings

# Setup Redis connection for RQ (valkey)
redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
queue = Queue('rag-queries', connection=redis_conn)

# Setup MongoDB connection
mongo_client = MongoClient(settings.MONGODB_URI)
db = mongo_client[settings.MONGODB_DB]
collection = db[settings.MONGODB_COLLECTION]

def process_query(job_id, query):
    """Process a RAG query job: update status, run retrieval, and store result."""
    collection.update_one({'job_id': job_id}, {'$set': {'status': 'processing'}}, upsert=True)
    try:
        result = retrieve_answer(query)
        # result is a dict with 'answer' and 'references'
        collection.update_one(
            {'job_id': job_id},
            {'$set': {'status': 'completed', 'answer': result.get('answer'), 'references': result.get('references')}},
            upsert=True
        )
    except Exception as e:
        collection.update_one({'job_id': job_id}, {'$set': {'status': 'failed', 'error': str(e)}}, upsert=True)
    return True

def run_worker():
    with Connection(redis_conn):
        worker = Worker([queue])
        worker.work()

if __name__ == '__main__':
    run_worker()