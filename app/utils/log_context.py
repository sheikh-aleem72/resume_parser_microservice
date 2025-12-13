from contextvars import ContextVar

job_id_ctx = ContextVar("job_id", default=None)
batch_id_ctx = ContextVar("batch_id", default=None)
resume_id_ctx = ContextVar("resume_id", default=None)

def set_log_context(jobId=None, batchId=None, resumeId=None):
    if jobId:
        job_id_ctx.set(jobId)
    if batchId:
        batch_id_ctx.set(batchId)
    if resumeId:
        resume_id_ctx.set(resumeId)

def get_log_context():
    return {
        "jobId": job_id_ctx.get(),
        "batchId": batch_id_ctx.get(),
        "resumeId": resume_id_ctx.get(),
    }
