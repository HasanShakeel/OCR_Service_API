import os
import redis.asyncio as redis
from fastapi import UploadFile
from dotenv import load_dotenv
from ..utils.log_function import logs
from ..services.perform_ocr import process_OCR

env_path = "backend/api/variables.env"
load_dotenv(env_path)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

# Create a redis connection pool
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Create a redis client with the connection pool
redis_client = redis.Redis(connection_pool=pool)

async def store_file_in_redis(file: UploadFile, document_id: int):
    """
    Store the processed OCR file in Redis.
    """
    try:
        file_contents = await file.read()  
        OCR_result = await process_OCR(file_contents)
        
        if OCR_result:
            # Convert BytesIO object to bytes
            processed_file_bytes = OCR_result.getvalue()
            
            await redis_client.set(f'file:{document_id}', processed_file_bytes)
            logs('info', f"Stored OCR processed file in Redis with document ID: {document_id}")
            print("File saved into Redis successfully")
        else:
            logs('error', "Failed to process OCR")
            print("Failed to process OCR")

    except Exception as e:
        logs('critical', "An error occurred", str(e))

