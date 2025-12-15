import networkx as nx

def build_graph(data):
    G = nx.DiGraph()

    for character in data["characters"]:
        name = character["name"]
        group = character.get("group", "Unknown")

        G.add_node(name, group=group)

        for relation in character.get("relations", []):
            rel_type = relation["type"]
            target = relation["target"]

            # Parent & mentor relations are reversed
            if rel_type in ["parent", "mentor"]:
                G.add_edge(target, name, type=rel_type)
            else:
                G.add_edge(name, target, type=rel_type)

    return G
