from collections import defaultdict

from data import base as data_base
from docs.base import Guide


def tenet_type_to_pretty(tenet_type: str) -> str:
    match tenet_type:
        case data_base.TENET_TYPE_PHILOSOPHY:
            pretty_tenet_type = "Philosophy (resources)"
        case data_base.TENET_TYPE_ADORATION:
            pretty_tenet_type = "Adoration (faith)"
        case data_base.TENET_TYPE_SOCIAL:
            pretty_tenet_type = "Social (happiness)"
        case _:
            raise ValueError(f"Unknown tenet type {tenet_type}")
    return pretty_tenet_type


def pretty_print_tenet(tenet: data_base.Tenet) -> str:
    return f"{tenet.name} ({tenet_type_to_pretty(tenet.type)})"


def pretty_print_list_of_tenets(tenets: list[data_base.Tenet]) -> str:
    return ", ".join(map(pretty_print_tenet, tenets))


def tradition_category_to_pretty(tradition_category: str):
    match tradition_category:
        case data_base.CATEGORY_ECONOMY_SUPER:
            return "Core Economy"
        case data_base.CATEGORY_ECONOMY:
            return "Economy"
        case data_base.CATEGORY_POWER:
            return "Power"
        case data_base.CATEGORY_STARTING:
            return "Commandment"
        case _:
            raise ValueError(f"Unknown tradition category: {tradition_category}")


def pretty_print_tradition(tradition: data_base.Tradition) -> str:
    return f"{tradition.name} ({tradition_category_to_pretty(tradition.category)})"


def pretty_print_list_of_traditions(traditions: list[data_base.Tradition]) -> str:
    return ", ".join(map(pretty_print_tradition, traditions))


class TraditionsGuide(Guide):
    def generate_content(self) -> str:
        return self.formatter.as_paragraphs([self.generate_introduction(), self.generate_traditions(), self.generate_closing()])

    def generate_introduction(self) -> str:
        introduction_1 = "This guide aims to give insight in the possible paths you can take with regard to traditions. Since, depending on your initial Commandment, not all traditions are available."
        introduction_2 = "The classifications for the traditions in the categories Core Economy, Economy and Power are based on the guide "
        url = self.formatter.as_url("here",  "https://steamcommunity.com/sharedfiles/filedetails/?id=2200883930")
        traditions_list = [self.formatter.as_url(tradition.name, self.formatter.as_index_key(tradition.name)) for tradition in data_base.TRADITIONS]
        return self.formatter.as_header("Introduction") + self.formatter.as_paragraphs([introduction_1, introduction_2 + url]) + self.formatter.as_bullet_list(traditions_list)

    def generate_traditions(self) -> str:
        return self.print_starting_traditions() + self.print_economy_super_traditions() + self.print_economy_traditions() + self.print_power_traditions()

    def generate_closing(self) -> str:
        return self.formatter.as_paragraphs(["""This is based on data collected by starting every commandment then taking the first tradition and checking which tenets were new compared to the initial commandment.
        When that was not enough, other specific paths were taken to get the same tradition as second choice such that no already-granted tenets overlapped.""",
                                             """I've also made a program in Python that can help navigate this structure, just run main.py."""])

    def print_reachable_from_this_tradition(self, tradition: data_base.Tradition) -> str:
        reachable_traditions: dict[data_base.Tradition, list[data_base.Tenet]] = defaultdict(list)
        for tenet in tradition.tenets:
            for new_tradition in tenet.traditions:
                if new_tradition.name != tradition.name:
                    reachable_traditions[new_tradition].append(tenet)
        col1_key = "Tradition"
        col2_key = "Can be reached through"
        headers = [col1_key, col2_key]
        content = []
        for reachable_tradition, reachable_via in reachable_traditions.items():
            content.append({col1_key: pretty_print_tradition(reachable_tradition), col2_key: pretty_print_list_of_tenets(reachable_via)})
        return self.formatter.as_subsubheader("Traditions reachable from this") + self.formatter.as_table(headers, content)

    def print_what_leads_to_this_tradition(self, target_tradition: data_base.Tradition):
        source_traditions: dict[str, list[data_base.Tradition]] = defaultdict(list)
        for tradition in data_base.TRADITIONS:
            if any(map(lambda t: any(map(lambda d: d.name == target_tradition.name, t.traditions)), tradition.tenets)):
                source_traditions[tradition.category].append(tradition)
        if not source_traditions:
            return ""
        col1_key = "Category"
        col2_key = "Traditions"
        headers = [col1_key, col2_key]
        content = []
        for tradition_category in [data_base.CATEGORY_STARTING, data_base.CATEGORY_ECONOMY_SUPER, data_base.CATEGORY_ECONOMY, data_base.CATEGORY_POWER]:
            content.append({col1_key: tradition_category_to_pretty(tradition_category), col2_key: pretty_print_list_of_traditions(source_traditions.get(tradition_category, []))})
        return self.formatter.as_subsubheader("Traditions that lead to this") + self.formatter.as_table(headers, content)

    def print_complete_tradition(self, tradition: data_base.Tradition):
        paragraphs = [self.formatter.as_bullet_list(tradition.effect)]

        tenet_by_type_dict = defaultdict(list)
        for tenet in tradition.tenets:
            tenet_by_type_dict[tenet.type].append(tenet)
        type_key = "Type"
        tenets_key = "Tenets"
        table = [{type_key: tenet_type_to_pretty(tenet_type), tenets_key: ', '.join(map(lambda t: t.name, tenet_by_type_dict[tenet_type]))} for tenet_type in [data_base.TENET_TYPE_ADORATION, data_base.TENET_TYPE_SOCIAL, data_base.TENET_TYPE_PHILOSOPHY]]
        paragraphs.append(self.formatter.as_subsubheader("Unlocks tenets") + self.formatter.as_table([type_key, tenets_key], table))
        paragraphs.append(self.print_what_leads_to_this_tradition(tradition))
        paragraphs.append(self.print_reachable_from_this_tradition(tradition))
        return self.formatter.as_subheader(tradition.name) + self.formatter.as_paragraphs(paragraphs)

    def _print_traditions_for_category(self, header: str, category: str):
        paragraphs = []
        for tradition in filter(lambda t: t.category == category, data_base.TRADITIONS):
            paragraphs.append(self.print_complete_tradition(tradition))
        return self.formatter.as_header(header) + self.formatter.as_paragraphs(paragraphs)

    def print_starting_traditions(self):
        return self._print_traditions_for_category("Commandments", data_base.CATEGORY_STARTING)

    def print_economy_super_traditions(self):
        return self._print_traditions_for_category("Core economy traditions", data_base.CATEGORY_ECONOMY_SUPER)

    def print_economy_traditions(self):
        return self._print_traditions_for_category("Other economy traditions", data_base.CATEGORY_ECONOMY)

    def print_power_traditions(self):
        return self._print_traditions_for_category("Power traditions", data_base.CATEGORY_POWER)
