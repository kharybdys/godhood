import json
import os
from dataclasses import dataclass, field
from functools import cached_property, cache

from src.base import GodhoodBase
from src.tree import build_tree

TENET_TYPE_ADORATION = "ADORATION"  # Faith + 10
TENET_TYPE_SOCIAL = "SOCIAL"  # Happiness + 2
TENET_TYPE_PHILOSOPHY = "PHILOSOPHY"  # Passive resources + 25

COLOR_YELLOW = "YELLOW"  # Greed
COLOR_BLUE = "BLUE"  # Purity
COLOR_CYAN = "CYAN"  # Peace
COLOR_PURPLE = "PURPLE"  # Madness
COLOR_GREEN = "GREEN"  # Generosity
COLOR_LIGHT_GREEN = "LIGHT_GREEN"  # Generosity
COLOR_RED = "RED"  # War
COLOR_PINK = "PINK"  # Pleasure
COLOR_ORANGE = "ORANGE"  # ?
COLOR_GREY = "GREY"  # ?

colors = [COLOR_YELLOW, COLOR_BLUE, COLOR_CYAN, COLOR_PURPLE, COLOR_GREEN, COLOR_LIGHT_GREEN, COLOR_RED, COLOR_PINK, COLOR_PURPLE, COLOR_ORANGE, COLOR_GREY]

CATEGORY_STARTING = "STARTING"
CATEGORY_ECONOMY_SUPER = "ECONOMY_SUPER"
CATEGORY_ECONOMY = "ECONOMY"
CATEGORY_POWER = "POWER"


@dataclass
class Tenet(GodhoodBase):
    type: str
    color: str
    events: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    tradition_names: list[str] = field(default_factory=list)

    @cached_property
    def traditions(self):
        result = []
        for tradition in TRADITIONS:
            if tradition.name in self.tradition_names:
                result.append(tradition)
        return result

    def related_data(self) -> list[GodhoodBase]:
        return self.traditions

    def __repr__(self):
        return f"{self.name} ({self.type})"

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


@dataclass
class Tradition(GodhoodBase):
    color: str
    category: str
    comment: str = None
    effect: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    tenet_names: list[str] = field(default_factory=list)

    @cached_property
    def tenets(self):
        result = []
        for tenet in TENETS:
            if tenet.name in self.tenet_names:
                result.append(tenet)
        return result

    def related_data(self) -> list[GodhoodBase]:
        return self.tenets

    def is_starting(self) -> bool:
        return self.category == CATEGORY_STARTING

    def __repr__(self):
        return f"{self.name} ({self.category})"

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


@dataclass
class Passive:
    name: str
    effect: str
    level: int


@dataclass
class Ability:
    name: str
    element: str
    type: str
    style: str
    effect: list[str] = field(default_factory=list)
    stats: list[str] = field(default_factory=list)


@dataclass
class GodhoodClass:
    name: str
    element: str
    availability: str
    de_buffs: str
    stats: list[str] = field(default_factory=list)
    passives: list[Passive] = field(default_factory=list)
    abilities: list[Ability] = field(default_factory=list)

    @cached_property
    def third_level_passives(self) -> (Passive, Passive, Passive):
        template_3rd_level_name = "# Up"
        template_3rd_level_effect = "+20% #"
        result = [Passive(name=template_3rd_level_name.replace("#", stat), effect=template_3rd_level_effect.replace("#", stat), level=3) for stat in self.stats]
        result.append(Passive(name="", effect="", level=3))
        return result

    def get_passives_for_level(self, level: int) -> (Passive, Passive, Passive):
        if level == 3:
            return self.third_level_passives
        passives = list(filter(lambda p: p.level == level, self.passives))
        return passives[0], passives[1], self.passive_3rd_choice(level)

    def passive_3rd_choice(self, level: int) -> Passive:
        first_stat = self.stats[0]
        second_stat = self.stats[1]
        third_choice_name = "#1 & #2 Up".replace("#1", first_stat).replace("#2", second_stat)
        third_choice_effect = "+5 #1 and +5 #2".replace("#1", first_stat).replace("#2", second_stat)
        return Passive(name=third_choice_name, effect=third_choice_effect, level=level)


def load_data():
    with open(os.path.join(os.path.dirname(__file__), "godhood.json"), "r") as data_file:
        data_dict = json.load(fp=data_file)
    tenets_result = []
    for tenet_dict in data_dict["tenets"]:
        tenets_result.append(Tenet(**tenet_dict))
    traditions_result = []
    for tradition_dict in data_dict["traditions"]:
        traditions_result.append(Tradition(**tradition_dict))
    classes_result = []
    for classes_dict in data_dict["classes"]:
        passives = [Passive(**passive_dict) for passive_dict in classes_dict.pop("passives")]
        abilities = [Ability(**ability_dict) for ability_dict in classes_dict.pop("abilities")]
        classes_result.append(GodhoodClass(**dict(**classes_dict, passives=passives, abilities=abilities)))

    # validate
    for tenet in tenets_result:
        for tradition_name in tenet.tradition_names:
            if tradition_name and not any(map(lambda t: t.name == tradition_name, traditions_result)):
                print(f"{tenet=} has unknown tradition {tradition_name}")
        if tenet.type not in [TENET_TYPE_SOCIAL, TENET_TYPE_ADORATION, TENET_TYPE_PHILOSOPHY]:
            print(f"{tenet=} has unknown type")
        if tenet.color not in colors:
            print(f"{tenet=} has unknown color")
        if not tenet.tradition_names or not all(tenet.tradition_names):
            if tenet.name in ["Nature & Animal Dedication", "Symbolic Dedication", "Celestial Dedication", "Dark Dedication"]:
                # Do not have any followup traditions
                pass
            else:
                print(f"Missing traditions on tenet {tenet.name}")
    for tradition in traditions_result:
        for tenet_name in tradition.tenet_names:
            if tenet_name and not any(map(lambda t: t.name == tenet_name, tenets_result)):
                print(f"{tradition=} has unknown tenet {tenet_name}")
        if tradition.category not in [CATEGORY_STARTING, CATEGORY_ECONOMY, CATEGORY_ECONOMY_SUPER, CATEGORY_POWER]:
            print(f"{tradition=} has unknown category")
        if tradition.color not in colors:
            print(f"{tradition=} has unknown color")
        if not tradition.tenet_names or not all(tradition.tenet_names):
            print(f"Missing tenets on tradition {tradition.name}")
        if not tradition.effect:
            print(f"Missing effect on tradition {tradition.name}")
    return tenets_result, traditions_result, classes_result


TENETS, TRADITIONS, CLASSES = load_data()


@cache
def get_data_tree(max_depth: int):
    return build_tree(list(filter(lambda t: t.category == CATEGORY_STARTING, TRADITIONS)), max_depth + 1)  # Because of the start
