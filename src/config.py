from dataclasses import dataclass, field
from typing import List, Union, Optional
import yaml


@dataclass
class Node:
    type: str
    width: Optional[int] = None
    nodes: List[Union["Node", None]] = field(default_factory=list)


def parse_node(data: dict) -> Node:
    """Recursively parse a dictionary into a Node object."""
    node_type = data.get("type")
    width = data.get("width")
    nodes = [parse_node(child) for child in data.get("nodes", [])]
    return Node(type=node_type, width=width, nodes=nodes)


def parse_yaml_to_tree(yaml_data: str) -> Node:
    """Parse the given YAML string into a tree of Node objects."""
    data = yaml.safe_load(yaml_data)
    return parse_node(data["nodes"][0])


# Example usage
yaml_data_example = """nodes:
  - type: vertical
    nodes:
      - width: 70
        type: horizontal
        nodes:
          - width: 60
            type: window
          - width: 40
            type: window
      - width: 25
        type: vertical
        nodes:
          - width: 50
            type: window
          - width: 50
            type: window
      - width: 5
        type: window
"""


def verify_tree(node: Node, path: str = "root") -> bool:
    """Recursively verify that the sum of widths in each group of nodes equals 100.
    Provides detailed information on where the issue occurs."""
    if not node.nodes:
        # Base case: No child nodes to verify, return True
        return True

    total_width = 0
    for index, child in enumerate(node.nodes):
        if child.width is not None:
            total_width += child.width

        # Recursively verify child nodes, adding to the path for better traceability
        if not verify_tree(child, path=f"{path} -> {child.type}[{index}]"):
            return False

    # Verify that the sum of widths is 100 if the node has children
    if total_width != 100:
        print(f"Error at {path}: Total width is {total_width}, but expected 100.")
        return False

    return True
