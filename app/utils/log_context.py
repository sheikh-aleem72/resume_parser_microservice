from contextvars import ContextVar

job_id_ctx = ContextVar("job_id", default=None)
batch_id_ctx = ContextVar("batch_id", default=None)
resume_processing_id_ctx = ContextVar("resume_processing_id", default=None)
external_resume_id_ctx = ContextVar("external_resume_id", default=None)

def set_log_context(jobId=None, batchId=None, resumeProcessingId=None, externalResumeId=None):
    if jobId:
        job_id_ctx.set(jobId)
    if batchId:
        batch_id_ctx.set(batchId)
    if resumeProcessingId:
        resume_processing_id_ctx.set(resumeProcessingId)
    if externalResumeId:
        external_resume_id_ctx.set(externalResumeId)

def get_log_context():
    return {
        "jobId": job_id_ctx.get(),
        "batchId": batch_id_ctx.get(),
        "resumeProcessingId": resume_processing_id_ctx.get(),
        "externalResumeId": external_resume_id_ctx.get()
    }
