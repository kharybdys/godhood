from data.base import GodhoodClass, CLASSES, Ability, Passive
from docs.base import Guide


class ClassesGuide(Guide):
    def generate_content(self) -> str:
        return self.formatter.as_paragraphs([self.generate_introduction(), self.generate_classes()])

    def generate_introduction(self) -> str:
        class_list = [self.formatter.as_url(cls.name, self.formatter.as_index_key(cls.name)) for cls in CLASSES]
        return self.formatter.as_header("Classes") + """This guide aims to give an overview of all classes.""" + self.formatter.as_bullet_list(class_list)

    def generate_classes(self) -> str:
        return self.formatter.as_paragraphs([self.generate_class(cls) for cls in CLASSES])

    def generate_class(self, cls: GodhoodClass) -> str:
        effects = ["Available: " + cls.availability, "Element: " + cls.element, "Stats: " + ", ".join(cls.stats), cls.de_buffs]
        return self.formatter.as_subheader(cls.name) + self.formatter.as_bullet_list(effects) + self.formatter.LINE_SEP + self.generate_abilities(cls) + self.generate_passives(cls)

    def generate_abilities(self, cls: GodhoodClass) -> str:
        return self.formatter.as_subsubheader("Abilities") + self.formatter.LINE_SEP.join([self.generate_ability(ability) for ability in cls.abilities])

    def generate_ability(self, ability: Ability) -> str:
        element_key = "Element"
        type_key = "Type"
        stats_key = "Stats"
        style_key = "Style"
        headers = [element_key, type_key, stats_key, style_key]
        table = [{element_key: ability.element, type_key: ability.type, stats_key: ability.stats, style_key: ability.style}]
        return self.formatter.LINE_SEP + self.formatter.as_subsubsubheader(ability.name) + self.formatter.as_table(headers, table) + self.formatter.LINE_SEP + self.formatter.LINE_SEP + ability.effect

    def generate_passives(self, cls: GodhoodClass) -> str:
        col1_key = "Choice 1"
        col2_key = "Choice 2"
        col3_key = "Choice 3"
        headers = [col1_key, col2_key, col3_key]
        table = []
        for level in range(2, 6):
            passive_1, passive_2, passive_3 = cls.get_passives_for_level(level)
            table.append({col1_key: self.generate_passive(passive_1), col2_key: self.generate_passive(passive_2), col3_key: self.generate_passive(passive_3)})
        return self.formatter.as_subsubheader("Passives") + self.formatter.as_table(headers, table)

    @staticmethod
    def generate_passive(passive: Passive) -> str:
        if passive.name == "":
            return ""
        return f"{passive.name}: {passive.effect}"
