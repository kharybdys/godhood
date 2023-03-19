from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self


@dataclass
class GodhoodBase(ABC):
    name: str

    @abstractmethod
    def related_data(self) -> list[Self]:
        pass

    def is_starting(self) -> bool:
        return False

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)
