import time
import os
import redis

# ENV CONFIG
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
RETRY_SET = os.getenv("RETRY_SET_KEY", "rq:retry")
QUEUE_NAME = os.getenv("RQ_QUEUE", "batch-processing")
POLL_INTERVAL = float(os.getenv("RETRY_SCHED_POLL_INTERVAL", "1"))  # seconds

# REDIS CONNECTION
r = redis.from_url(REDIS_URL)

def move_due_jobs():
    """Moves jobs whose retry time has arrived back into the main queue."""
    now = int(time.time())

    # Get all job IDs with score <= now (retry time reached)
    job_ids = r.zrangebyscore(RETRY_SET, 0, now)

    if not job_ids:
        return 0

    # Move back to processing queue atomically
    pipeline = r.pipeline()
    for job_id in job_ids:
        pipeline.lpush(f"rq:queue:{QUEUE_NAME}", job_id)
        pipeline.zrem(RETRY_SET, job_id)
    pipeline.execute()

    print(f"↪ Re-queued {len(job_ids)} job(s) at time {now}")
    return len(job_ids)


if __name__ == "__main__":
    print("⏳ Retry Scheduler Started")
    print(f"Watching ZSET: {RETRY_SET}")

    while True:
        try:
            move_due_jobs()
        except Exception as e:
            print(f"⚠ Scheduler error: {e}")

        time.sleep(POLL_INTERVAL)
