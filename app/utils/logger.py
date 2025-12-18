import logging
from app.utils.log_context import get_log_context

class ContextFormatter(logging.Formatter):
    def format(self, record):
        ctx = get_log_context()
        context_str = " ".join(
            f"{k}={v}" for k, v in ctx.items() if v is not None
        )

        record.context = context_str
        return super().format(record)


def setup_logger():
    logger = logging.getLogger("resume-worker")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = ContextFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(context)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent duplicate logs
    logger.propagate = False

    return logger


logger = setup_logger()
