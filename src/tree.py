from collections import deque, defaultdict
from dataclasses import field, dataclass
from functools import partial
from typing import Tuple, Callable, Any, Self

from base import GodhoodBase


@dataclass
class DummyGodhoodBase(GodhoodBase):
    data: list[GodhoodBase] = field(default_factory=list)

    def related_data(self) -> list[GodhoodBase]:
        return self.data

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


class Node:
    def __init__(self, data: GodhoodBase, seen_tenets: set[GodhoodBase] = None, reachable_via: list[GodhoodBase] = None, output_mode: str = None):
        self.key = data.name
        self.tradition = data
        self.reachable_via: list[GodhoodBase] = reachable_via or []
        self.children: list[Node] = []
        self.seen_tenets: set[GodhoodBase] = seen_tenets or set()
        self.output_mode = output_mode or ("STARTING" if data.is_starting() else "")

    def __repr__(self):
        return f"Node[{self.key}, reachable_via: {self.reachable_via}, seen_tenets: {self.seen_tenets}, children: {self.children}]"

    @staticmethod
    def construct_starting_node(starting_traditions: list[GodhoodBase]) -> Self:
        def wrap_tradition(tradition: GodhoodBase) -> GodhoodBase:
            return DummyGodhoodBase(data=[tradition], name="Start tenet to " + tradition.name)
        return Node(data=DummyGodhoodBase(data=[wrap_tradition(tradition) for tradition in starting_traditions], name="Start"), output_mode="SUPPRESS")


def build_tree(starting_traditions: list[GodhoodBase], max_depth: int = 7) -> Node:

    start_node = Node.construct_starting_node(starting_traditions=starting_traditions)
    nodes_to_visit: deque[Tuple[Node, int, list[str]]] = deque()
    nodes_to_visit.append((start_node, 0, []))
    while len(nodes_to_visit) > 0:
        current_node, current_depth, visited_keys = nodes_to_visit.popleft()
        new_visited_keys = visited_keys + [current_node.key]
        if current_depth < max_depth:
            reachable_traditions = defaultdict(list)
            for tenet in current_node.seen_tenets.union(current_node.tradition.related_data()):
                for new_tradition in tenet.related_data():
                    if new_tradition.name not in new_visited_keys:
                        reachable_traditions[new_tradition].append(tenet)
            for new_tradition, reachable_via in reachable_traditions.items():
                new_seen_tenets: set[GodhoodBase] = set(current_node.seen_tenets)
                new_seen_tenets.update(new_tradition.related_data())
                new_node = Node(new_tradition, new_seen_tenets, reachable_via)
                current_node.children.append(new_node)
                nodes_to_visit.append((new_node, current_depth + 1, new_visited_keys))

    return start_node


def print_path_at_condition(condition_function: Callable, node: Node, obj: Any) -> (bool, Any):
    if node.output_mode == "SUPPRESS":
        new_obj = obj
    else:
        prefix = f"{obj}, " if obj else ""
        new_obj = f"{prefix}{node.key}"
        if not node.output_mode == "STARTING":
            new_obj = f"{new_obj} (reachable via {node.reachable_via})"
    if condition_function(node, obj):
        print(f"Seen nodes is: {sorted([t.name for t in node.seen_tenets])}")
        print(f"Path is {new_obj}")
        return True, new_obj
    else:
        return False, new_obj


def print_all_paths_to_tradition_name(start_node: Node, name: str):
    def at_tradition_name(node: Node, obj: Any) -> bool:
        return any(map(lambda t: t.key == name, node.children))

    breadth_first_traversal(start_node, partial(print_path_at_condition, at_tradition_name))


def print_tree(start_node: Node):
    def no_children(node: Node, obj: Any) -> bool:
        return not node.children

    breadth_first_traversal(start_node, partial(print_path_at_condition, no_children))


def breadth_first_traversal(start_node: Node, visit_function: Callable):
    nodes_to_visit: deque[Tuple[Node, Any]] = deque()
    nodes_to_visit.append((start_node, None))
    while len(nodes_to_visit) > 0:
        current_node, obj = nodes_to_visit.popleft()
        should_stop, new_obj = visit_function(current_node, obj)
        if not should_stop:
            for child in current_node.children:
                nodes_to_visit.append((child, new_obj))
