from abc import ABC, abstractmethod


class GraphPort(ABC):
    @abstractmethod
    def query(self, cypher: str, params: dict | None = None) -> list[dict]:
        raise NotImplementedError
