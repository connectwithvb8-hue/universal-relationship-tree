import networkx as nx


def build_graph(records):
    G = nx.DiGraph()

    for item in records:
        person = item["character"]
        relation = item["relationship"]
        relative = item["relative"]

        if not person or not relation or not relative:
            continue

        if not G.has_node(person):
            G.add_node(person)

        if not G.has_node(relative):
            G.add_node(relative)

        if not G.has_edge(person, relative):
            G.add_edge(person, relative, type=relation)

    return G
