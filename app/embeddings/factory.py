# from app.embeddings.providers.gemini import GeminiEmbeddingProvider
from app.embeddings.providers.minilm import MiniLMEmbeddingProvider


def get_embedding_provider(provider_name: str):
    if provider_name == "minilm":
        return MiniLMEmbeddingProvider()

    # if provider_name == "gemini":
    #     return GeminiEmbeddingProvider()

    raise ValueError(f"Unknown embedding provider: {provider_name}")

