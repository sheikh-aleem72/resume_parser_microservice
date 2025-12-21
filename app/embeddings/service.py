from app.embeddings.factory import get_embedding_provider


def generate_embedding(text: str, provider_name: str = "minilm"):
    provider = get_embedding_provider(provider_name)
    embedding = provider.embed(text)
    return embedding, provider.model_name
