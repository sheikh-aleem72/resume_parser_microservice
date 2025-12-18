import requests
import tempfile
import mimetypes
import os

def download_resume(resume_url: str):
    """
    Downloads resume from Cloudinary and stores it as a temporary file.
    Returns: (local_path, mime_type)
    """
    response = requests.get(resume_url, stream=True)
    response.raise_for_status()

    suffix = os.path.splitext(resume_url)[1] or ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(response.content)
    tmp.close()

    mime = mimetypes.guess_type(tmp.name)[0] or "application/octet-stream"

    return tmp.name, mime
