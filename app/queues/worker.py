import json
import os
import time
import redis
import requests
from rq import Worker, Queue, job
from pymongo import MongoClient

# ------------------------------
# ENV CONFIG
# ------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:5000/api/v1/batch/update")
MONGO_URI = os.getenv("MONGO_URI_PY", "mongodb://localhost:27017/resume_screener_dev")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BASE_DELAY = int(os.getenv("BASE_DELAY_SECONDS", "5"))
RETRY_SET = os.getenv("RETRY_SET_KEY", "rq:retry")
QUEUE_NAME = os.getenv("RQ_QUEUE", "batch-processing")

# ------------------------------
# CONNECTIONS
# ------------------------------
redis_conn = redis.from_url(REDIS_URL)
mongo = MongoClient(MONGO_URI)
db = mongo["resume_screener_dev"]
batches = db["batches"]

queue = Queue(QUEUE_NAME, connection=redis_conn)


class JSONWorker(Worker):

    def execute_job(self, job: job, queue):
        """Executes a single resume-processing job with retry + safe callbacks."""

        # Load payload
        data = json.loads(job.data)

        batch_id = data["batchId"]
        resume_id = data["resumeId"]
        resume_url = data.get("resumeUrl")
        job_redis_key = f"rq:job:{job.id}"
        print("================================================================")
        print(f"\n🚀 START Job {job.id} | Resume {resume_id} | Batch {batch_id}")

        # ------------------------------
        # STEP 1 — Update resume status to PROCESSING in Mongo
        # ------------------------------
        try:
            batches.update_one(
                {"batchId": batch_id, "resumes.resumeId": resume_id},
                {"$set": {"resumes.$.status": "processing"}}
            )
            print(f"⚙️ Mongo update: resume {resume_id} → processing")

        except Exception as e:
            print(f"❌ Failed to set processing state: {e}")

        

        # ------------------------------
        # STEP 2 — PROCESS RESUME (core logic)
        # ------------------------------
        try:
            print(f"📄 Processing URL: {resume_url}")
            print("🧠 Simulating resume analysis...")


            # -------------------------------------------
            # TODO: place real resume processing logic here
            # -------------------------------------------

            processing_status = "completed"
            error_msg = None

        except Exception as e:
            processing_status = "failed"
            error_msg = str(e)
            print(f"❌ Processing error: {error_msg}")

        # ------------------------------
        # STEP 3 — Handle SUCCESS or RETRY/FAILURE
        # ------------------------------

        # CASE 1 → Resume processing FAILED
        if processing_status == "failed":
            # increase attempts counter
            attempts = redis_conn.hincrby(job_redis_key, "attempts", 1)

            if attempts <= MAX_RETRIES:
                # schedule retry using exponential backoff
                delay = BASE_DELAY * (2 ** (attempts - 1))
                next_time = int(time.time()) + delay

                redis_conn.zadd(RETRY_SET, {job.id: next_time})

                print(
                    f"↻ Retry {attempts}/{MAX_RETRIES} scheduled for Job {job.id} "
                    f"after {delay}s (resume {resume_id})"
                )

                # DO NOT send callback (resume not done yet)
                return True

            else:
                # Max retries reached → mark as permanent failure
                print(f"✖ Max retries reached for Resume {resume_id}")

                # FINAL failure callback to Node
                try:
                    requests.post(CALLBACK_URL, json={
                        "batchId": batch_id,
                        "resumeId": resume_id,
                        "status": "failed",
                        "error": error_msg
                    })
                    print(f"📩 Final FAILED callback sent → resume {resume_id}")

                except Exception as cb_err:
                    print(f"⚠ Callback sending failed (max retries exhausted): {cb_err}")

                # cleanup redis job data
                # redis_conn.delete(job_redis_key)
                redis_conn.zrem(RETRY_SET, job.id)

                return True

        # CASE 2 → Resume processing SUCCESS
        try:
            res = requests.post(CALLBACK_URL, json={
                "batchId": batch_id,
                "resumeId": resume_id,
                "status": "completed",
                "error": None
            })

            if res.status_code == 200:
                print(f"✅ SUCCESS callback sent → resume {resume_id}")
            else:
                print(f"⚠ Callback HTTP error: {res.status_code} → {res.text}")

        except Exception as cb_err:
            # IMPORTANT: callback failure ❗DO NOT retry processing
            print(f"⚠ Callback network error (resume completed): {cb_err}")

        # Cleanup Redis job data
        redis_conn.delete(job_redis_key)

        print(f"🏁 FINISHED Job {job.id}\n")
        return True


if __name__ == "__main__":
    print(f"👷 Worker started — listening on queue: {QUEUE_NAME}")
    worker = JSONWorker([queue], connection=redis_conn)
    worker.work()
