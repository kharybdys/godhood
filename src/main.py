import os
from collections import defaultdict
from typing import Iterable

from data.base import Tradition, TRADITIONS, Tenet, TENETS, get_data_tree
from docs.classes import ClassesGuide
from docs.events import EventsGuide
from docs.formatters import MarkdownFormatter
from docs.traditions import TraditionsGuide
from tree import print_all_paths_to_tradition_name, print_tree


def find_tenet_by_name(name: str) -> Tenet:
    for tenet in TENETS:
        if tenet.name.upper() == name.upper():
            return tenet


def find_tradition_by_name(name: str) -> Tradition:
    for tradition in TRADITIONS:
        if tradition.name.upper() == name.upper():
            return tradition


def names_to_traditions(names: Iterable[str], all_traditions: list[Tradition]) -> list[Tradition]:
    result = []
    for tradition in all_traditions:
        if tradition.name in names:
            result.append(tradition)
    return result


def validate_tradition_path(tradition_path: list[Tradition]) -> bool:
    used_traditions = tradition_path[0:1]
    available_tenets: set[Tenet] = set()
    for tenet in used_traditions[0].tenets:
        available_tenets.add(tenet)
    for tradition in tradition_path[1:]:
        tenets_to_this_tradition = list(filter(lambda t: tradition.name in t.tradition_names, available_tenets))
        if tenets_to_this_tradition:
            print(f"Valid tenets to tradition {tradition.name} are: {tenets_to_this_tradition}")
            available_tenets.update(tradition.tenets)
            if len(tenets_to_this_tradition) == 1 and tenets_to_this_tradition[0].blocks:
                available_tenets = {t for t in available_tenets if t.name not in tenets_to_this_tradition[0].blocks}
                available_tenets.add(tenets_to_this_tradition[0])
            used_traditions.append(tradition)
        else:
            print(f"Tradition {tradition.name} not reachable from: {used_traditions}")
            return False
    return True


def print_next_reachable_traditions(tradition_path: list[Tradition]):
    if validate_tradition_path(tradition_path):
        available_traditions = set()
        for tradition in tradition_path:
            for tenet in tradition.tenets:
                for new_tradition in tenet.traditions:
                    if new_tradition not in tradition_path:
                        available_traditions.add(new_tradition)
        print("Next reachable tradition is one of:")
        result = defaultdict(list)
        for tradition in available_traditions:
            result[tradition.category].append(tradition.name)
        for category, traditions in result.items():
            print(f"{category}: {traditions}")


def check_next_reachable_traditions():
    valid_input = False
    while not valid_input:
        taken_tradition_names = list(map(lambda s: s.strip(), input("Provide your taken traditions in order (use , to separate): ").split(",")))
        if all(map(lambda name: name in map(lambda t: t.name, TRADITIONS), taken_tradition_names)):
            valid_input = True
            taken_traditions = names_to_traditions(taken_tradition_names, TRADITIONS)
            print_next_reachable_traditions(taken_traditions)
        else:
            print("Invalid tradition(s) specified. Valid tradition names are:")
            print(TRADITIONS)


def ask_for_max_depth() -> int:
    while True:
        max_depth_str = input("How many traditions may be chained? ")
        try:
            max_depth = int(max_depth_str)
            if 0 < max_depth < 10:
                return max_depth
        except ValueError:
            pass
        print("Invalid input, please enter a number between 0 and 10")


def reach_tradition():
    valid_input = False
    while not valid_input:
        tradition_name = input("Provide the tradition name you want to reach: ").strip()
        if tradition := find_tradition_by_name(tradition_name):
            valid_input = True
            max_depth = ask_for_max_depth()
            print_all_paths_to_tradition_name(get_data_tree(max_depth), tradition.name)
        else:
            print("Invalid input, try again.")


def print_data_tree():
    max_depth = ask_for_max_depth()
    print_tree(get_data_tree(max_depth))


def write_guides():
    docs_dir = os.path.join(os.path.dirname(__file__), "../docs")
    ClassesGuide(output_path=os.path.join(docs_dir, "CLASSES.md"), formatter=MarkdownFormatter()).write_output()
    EventsGuide(output_path=os.path.join(docs_dir, "EVENTS.md"), formatter=MarkdownFormatter()).write_output()
    TraditionsGuide(output_path=os.path.join(docs_dir, "TRADITIONS.md"), formatter=MarkdownFormatter()).write_output()


FUNCTION = "function"
DESCRIPTION = "description"

OPTIONS = {"1": {FUNCTION: check_next_reachable_traditions, DESCRIPTION: "Find the next reachable traditions given a tradition path?"},
           "2": {FUNCTION: reach_tradition, DESCRIPTION: "List all paths to reach a given tradition?"},
           "3": {FUNCTION: print_data_tree, DESCRIPTION: "Print the tradition tree?"},
           "4": {FUNCTION: write_guides, DESCRIPTION: "Update all Markdown guides"}
           }

print("What do you want to do?")
for key, value in OPTIONS.items():
    print(f"[{key}] {value[DESCRIPTION]}")
valid = False
while not valid:
    choice = input("")
    if choice in OPTIONS.keys():
        valid = True
        OPTIONS[choice][FUNCTION]()
    else:
        print("Invalid input, try again.")
