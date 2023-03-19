from abc import ABC, abstractmethod

from docs.formatters import Formatter


class Guide(ABC):
    def __init__(self, formatter: Formatter, output_path: str):
        self.formatter = formatter
        self.output_path = output_path

    @abstractmethod
    def generate_content(self):
        pass

    def write_output(self):
        with open(self.output_path, "wt") as file:
            file.write(self.generate_content())
