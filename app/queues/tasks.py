import time
import random

def process_batch(data):
    print(f"🎯 Received batch job: {data.get('jobId')}")
    resumes = data.get("resumes", [])
    for resume in resumes:
        print(f"🧠 Parsing {resume} ...")
        time.sleep(random.uniform(1, 2))
    print("✅ Batch processing completed.")
