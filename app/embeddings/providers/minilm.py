from sentence_transformers import SentenceTransformer
from app.embeddings.providers.base import EmbeddingProvider


class MiniLMEmbeddingProvider(EmbeddingProvider):
    """
    Free, local embedding provider
    Model: sentence-transformers/all-MiniLM-L6-v2
    """

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    # IMPORTANT: load model once per worker process
    _model = None

    def __init__(self):
        if MiniLMEmbeddingProvider._model is None:
            MiniLMEmbeddingProvider._model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        try:
            embedding = MiniLMEmbeddingProvider._model.encode(
                text,
                normalize_embeddings=True  # VERY IMPORTANT for cosine similarity
            )

            # Convert numpy array → Python list
            return embedding.tolist()

        except Exception as e:
            raise RuntimeError(f"MiniLM embedding failed: {str(e)}") from e
