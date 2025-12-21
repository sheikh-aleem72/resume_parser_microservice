
class EmbeddingProvider:
    model_name: str

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError
