import json
import os
import redis
import requests
from rq import Worker, Queue, job
# from app.processor import process_batch  # your real batch logic

redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
callback_url = os.getenv("CALLBACK_URL", "http://localhost:5000/api/v1/batch/update")

conn = redis.from_url(redis_url)
QUEUE_NAME = "batch-processing"


class JSONWorker(Worker):
    def execute_job(self, job: job, queue):
        raw_payload = job.data
        data = json.loads(raw_payload)

        batch_id = data["batchId"]
        job_description_id = data["jobDescriptionId"]
        resumeId = data["resumeId"]
        resumeUrl = data["resumeUrl"] # can be null

        print(f"🎯 Processing resume {resumeId} (Batch: {batch_id})")
        print(f"📄 Resume URL: {resumeUrl}")

        # --- your actual processing logic ---
        try:
            # process_batch(batch_id, job_description_id, resumes)
            print("🧠 Simulating processing...")
            # time.sleep(2)
            
            status = "completed"
            error = None

        except Exception as e:
            status = "failed"
            error = str(e)
            print(f"❌ Error: {error}")

        print("📨 Sending callback to Node...")
        try:
            res = requests.post(callback_url, json={
                "batchId": batch_id,
                "resumeId": resumeId,
                "status": status,
                "error": error
            })

            if res.status_code == 200:
                print(f"✅ Callback sent successfully for {resumeId}\n")
            else:
                print(f"⚠ Callback failed: {res.status_code} → {res.text}")

        except Exception as e:
            print(f"❌ Callback: {e}")

        return True


if __name__ == "__main__":
    print(f"🚀 RQ Worker started. Listening on queue: {QUEUE_NAME}")

    queue = Queue(QUEUE_NAME, connection=conn)
    worker = JSONWorker([queue], connection=conn)
    worker.work()
