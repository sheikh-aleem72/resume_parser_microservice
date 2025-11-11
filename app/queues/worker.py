import redis
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
r = redis.from_url(redis_url)

CHANNEL = "batch-processing"

print(f"🚀 Worker listening on channel: {CHANNEL}")

pubsub = r.pubsub()
pubsub.subscribe(CHANNEL)

for message in pubsub.listen():
    if message["type"] != "message":
        continue

    try:
        data = json.loads(message["data"])
        batch_id = data.get("batchId")
        job_id = data.get("jobId")
        resumes = data.get("resumes", [])

        print(f"🎯 Received batch job: {batch_id} (for job: {job_id})")

        for resume in resumes:
            print(f"🧠 Parsing {resume} ...")
            time.sleep(1)  # simulate processing

        print("✅ Batch processing completed.\n")

    except Exception as e:
        print("❌ Error processing message:", e)
