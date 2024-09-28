import math

from flask import Flask, request, jsonify

from routes import app

import math

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the level of the logger

# Create a file handler
file_handler = logging.FileHandler('app.kazuma.log')  # Name of the file where logs will be written
file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)  # Apply the formatter to the handler

# Add the file handler to the logger
logger.addHandler(file_handler)

class Node:
    def __init__(self, state, gold):
        self.state = state  # "charged", "uncharged"
        self.gold = gold  # Current gold
        self.children = []  # List of child nodes (next possible actions)

    def add_child(self, child_node):
        self.children.append(child_node)


def build_tree(node, monsters, idx):
    # Base case: if no more enemies, stop building the tree
    if idx >= len(monsters):
        return

    # Branching from "uncharged"
    if node.state == "uncharged":
        # Kazuma can either remain at base or charge
        uncharge_node = Node("uncharged", node.gold)
        charge_node = Node("charged", node.gold - monsters[idx])  # Charge, losing current monster gold
        node.add_child(uncharge_node)
        node.add_child(charge_node)

        # Recursively build from these states
        build_tree(uncharge_node, monsters, idx + 1)
        build_tree(charge_node, monsters, idx + 1)

    # Branching from "charged"
    elif node.state == "charged":
        # Kazuma can either stay (remain charging) or attack
        uncharge_node = Node("uncharged", node.gold + monsters[idx])  # Attack, gaining monster gold
        charge_node = Node("charged", node.gold)  # Stay charged
        node.add_child(uncharge_node)
        node.add_child(charge_node)

        # Recursively build from these states
        build_tree(uncharge_node, monsters, idx + 1)
        build_tree(charge_node, monsters, idx + 1)


def build_kazuma_tree(monsters):
    root = Node("uncharged", 0)  # Start at base with 0 gold and the first enemy
    build_tree(root, monsters, 0)
    return root


# Traverse the tree and find the highest gold value
def find_max_gold(node):
    # Base case: if this node has no children, return its gold value
    if not node.children:
        return node.gold

    # Recurse through children to find the maximum gold value
    return max(find_max_gold(child) for child in node.children)


@app.route('/efficient-hunter-kazuma', methods=['POST'])
def efficient_hunter_kazuma():
    data = request.get_json()
    results = []

    for entry in data:
        monsters = entry["monsters"]
        tree_root = build_kazuma_tree(monsters)
        max_gold = find_max_gold(tree_root)
        results.append({"efficiency": max_gold})

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
