import json
import os
import time
import redis
import requests
from rq import Worker, Queue, job
from app.services.tasks import process_resume
from app.utils.log_context import set_log_context
from app.utils.logger import logger
from app.utils.mongo import resume_processings_collection
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv(f".env.{os.getenv('ENV', 'development')}")
# ------------------------------
# ENV CONFIG
# ------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:5000/api/v1/processing/callback")
MONGO_URI = os.getenv("MONGO_URI_PY", "mongodb://localhost:27017/resume_screener_dev")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BASE_DELAY = int(os.getenv("BASE_DELAY_SECONDS", "5"))
RETRY_SET = os.getenv("BATCH_RETRY_SET", "rq:retry")
QUEUE_NAME = os.getenv("BATCH_QUEUE_NAME", "batch-processing")

# ------------------------------
# CONNECTIONS
# ------------------------------
redis_conn = redis.from_url(REDIS_URL)
queue = Queue(QUEUE_NAME, connection=redis_conn)


class JSONWorker(Worker):

    def execute_job(self, job: job, queue):
        """Executes a single resume-processing job with retry + safe callbacks."""

        # Load payload
        payload = json.loads(job.data)

        resume_processing_id = payload["resumeProcessingId"]
        batch_id = payload["batchId"]
        external_resume_id = payload["externalResumeId"]

        job_redis_key = f"rq:job:{job.id}"

        set_log_context(
            jobId=job_redis_key,
            batchId=batch_id,
            resumeProcessingId=resume_processing_id,
            externalResumeId=external_resume_id
        )

        logger.info(f"🚀 Job started{job.id} | Resume {external_resume_id} | Batch {batch_id}\n")
        logger.info("\n\n=========================================================")

        try:
            # ------------------------------
            # STEP 1 — Update resume status to PROCESSING in Mongo
            # ------------------------------
            resume_processings_collection.update_one(
                {"_id": ObjectId(resume_processing_id)},
                {"$set": {"status": "processing"}}
            )

            logger.info(f"⚙️ Mongo update: resume {external_resume_id} → processing\n\n")

        except Exception as e:
            print(f"❌ Failed to set processing state: {e}")

        
        try:
            # ------------------------------
            # STEP 2 — execute business logic
            # ------------------------------
            result = process_resume(payload)


            # ------------------------------
            # STEP 3 — mark COMPLETED
            # ------------------------------
            resume_processings_collection.update_one(
                {"_id": ObjectId(resume_processing_id)},
                {"$set": {"status": "completed"}}
            )

            # ------------------------------
            # STEP 4 — final callback
            # ------------------------------
            self._send_callback(
                batch_id=batch_id,
                resume_processing_id=resume_processing_id,
                status="completed",
                external_resume_id=external_resume_id
            )

            # Cleanup redis job
            redis_conn.delete(job_redis_key)

            logger.info("✅ Job completed successfully\n")
            return True

        except Exception as err:
            logger.exception("❌ Job failed")

            # ------------------------------
            # STEP 5 — retry or fail
            # ------------------------------
            attempts = redis_conn.hincrby(job_redis_key, "attempts", 1) 

            if attempts <= MAX_RETRIES:
                delay = BASE_DELAY * (2 ** (attempts - 1))
                next_time = int(time.time()) + delay

                redis_conn.zadd(RETRY_SET, {job.id: next_time})

                logger.warning(
                    f"↻ Retry scheduled (attempt {attempts}/{MAX_RETRIES}) "
                    f"after {delay}s"
                    f"Resume: {external_resume_id}"
                )

                # DO NOT mark failed
                return True  

            # ------------------------------
            # STEP 6 — permanent FAILURE
            # ------------------------------
            resume_processings_collection.update_one(
                {"_id": ObjectId(resume_processing_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(err)
                    }
                }
            )

            self._send_callback(
                batch_id=batch_id,
                resume_processing_id=resume_processing_id,
                status="failed",
                external_resume_id=external_resume_id
            )

            redis_conn.zrem(RETRY_SET, job.id)
            redis_conn.delete(job_redis_key)

            logger.error("✖ Job permanently failed")
            return True


    def _send_callback(self, batch_id, resume_processing_id, status, external_resume_id):
        """
        Final callback only (success or permanent failure).
        """
        try:
            requests.post(
                CALLBACK_URL,
                json={
                    "batchId": batch_id,
                    "resumeProcessingId": resume_processing_id,
                    "status": status,
                    "externalResumeId": external_resume_id
                },
                timeout=5,
            )
            logger.info("📩 Callback sent\n")

        except Exception as e:
            # Callback failure should NOT retry processing
            logger.warning(f"⚠ Callback failed: {e}\n")


if __name__ == "__main__":
    logger.info(f"👷Batch Worker started — queue: {QUEUE_NAME}\n")
    worker = JSONWorker([queue], connection=redis_conn)
    worker.work()


