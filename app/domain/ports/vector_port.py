from abc import ABC, abstractmethod


class VectorPort(ABC):
    @abstractmethod
    def similarity_search(self, query: str, k: int) -> list[dict]:
        raise NotImplementedError
