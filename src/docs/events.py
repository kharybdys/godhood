from docs.base import Guide
from data.base import TRADITIONS, TENETS


class EventsGuide(Guide):
    def generate_content(self) -> str:
        return self.formatter.as_paragraphs([self.generate_introduction(), self.generate_events()])

    def generate_introduction(self) -> str:
        introduction_1 = "This guide is a collection of the observed events, grouped by related tenet or commandment. "
        introduction_2 = "Events are the small boni and penalties you can get. "
        return self.formatter.as_header("Introduction") + introduction_1 + introduction_2

    def generate_events(self) -> str:
        return self.generate_commandment_events() + self.generate_tenet_events()

    def generate_commandment_events(self):
        paragraphs = []
        for tradition in filter(lambda t: t.events, TRADITIONS):
            paragraphs.append(self.formatter.as_subheader(tradition.name) + self.formatter.as_bullet_list(tradition.events))
        return self.formatter.as_header("Commandments") + self.formatter.as_paragraphs(paragraphs)

    def generate_tenet_events(self):
        paragraphs = []
        for tenet in filter(lambda t: t.events, TENETS):
            paragraphs.append(self.formatter.as_subheader(tenet.name) + self.formatter.as_bullet_list(tenet.events))
        return self.formatter.as_header("Tenets") + self.formatter.as_paragraphs(paragraphs)
