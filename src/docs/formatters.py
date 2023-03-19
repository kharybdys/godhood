import os
from abc import ABC, abstractmethod


class Formatter(ABC):
    LINE_SEP = "\n"

    @abstractmethod
    def as_table(self, headers: list[str], content: list[dict[str, str]], skip_headers: bool = False) -> str:
        pass

    @abstractmethod
    def as_bullet_list(self, content: list[str]) -> str:
        pass

    @abstractmethod
    def as_paragraphs(self, content: list[str]) -> str:
        pass

    @abstractmethod
    def as_header(self, content: str, level: int = 1) -> str:
        pass

    def as_subheader(self, content: str) -> str:
        return self.as_header(content, 2)

    def as_subsubheader(self, content: str) -> str:
        return self.as_header(content, 3)

    def as_subsubsubheader(self, content: str) -> str:
        return self.as_header(content, 4)

    @abstractmethod
    def as_url(self, content: str, url: str) -> str:
        pass


class MarkdownFormatter(Formatter):
    @staticmethod
    def _join_incl_outsides(separator: str, content: list[str]):
        return separator + separator.join(content) + separator

    @staticmethod
    def _join_incl_start(separator: str, content: list[str]):
        return separator + separator.join(content)

    def as_table(self, headers: list[str], content: list[dict[str, str]], skip_headers: bool = False) -> str:
        lines = []
        col_sep = "|"
        if not skip_headers:
            lines.append(self._join_incl_outsides(col_sep, headers))
        lines.append(self._join_incl_outsides(col_sep, ["---" for _ in headers]))
        for content_line in content:
            lines.append(self._join_incl_outsides(col_sep, [content_line.get(header, "") for header in headers]))
        return self.LINE_SEP + self.LINE_SEP + self.LINE_SEP.join(lines)

    def as_bullet_list(self, content: list[str]) -> str:
        return self._join_incl_start(f"{self.LINE_SEP}* ", content)

    def as_paragraphs(self, content: list[str]) -> str:
        return f"{self.LINE_SEP}".join(content)

    def as_header(self, content: str, level: int = 1) -> str:
        header_marker = "#" * level
        return f"{self.LINE_SEP}{header_marker} {content}{self.LINE_SEP}"

    def as_url(self, content: str, url: str) -> str:
        return f"[{content}]({url})"
