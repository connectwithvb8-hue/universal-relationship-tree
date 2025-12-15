import streamlit as st
import networkx as nx
from graphviz import Digraph

from loaders import load_csv, load_json
from graph_builder import build_graph

SAFE_RELATIONS = {
    "father", "mother", "son", "daughter",
    "grandfather", "grandmother",
    "grandson", "granddaughter",
    "adoptive father", "adoptive mother",
    "adoptive son", "adoptive daughter",
    "friend", "spouse"
}

MAX_EDGES = 500

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Relation Fandom",
    page_icon="",
    layout="wide"
)

# ---------------- Minimal CSS (no layout hacks) ----------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.title(" Relation Fandom")
st.caption(
    "Stable family tree viewer. Scroll to explore. "
    "On mobile, use browser zoom if needed."
)

# ---------------- Sidebar ----------------
with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload CSV or JSON",
        type=["csv", "json"]
    )

    person_a_input = st.text_input("Person A")
    person_b_input = st.text_input("Person B")
    search_clicked = st.button("Search Relationship")

# ---------------- Upload Guard (KEPT AS REQUESTED) ----------------
if not uploaded_file:
    st.info("Upload a file to continue.")
    st.stop()

# ---------------- Load Data ----------------
if uploaded_file.name.lower().endswith(".json"):
    data = load_json(uploaded_file)
else:
    data = load_csv(uploaded_file)

graph = build_graph(data)

# ---------------- Helpers ----------------
name_lookup = {n.lower(): n for n in graph.nodes()}

def normalize(name):
    if not name:
        return None
    return name_lookup.get(name.strip().lower())

# ---------------- Tabs ----------------
tab_tree, tab_relation = st.tabs(
    ["Family Tree", "How Are They Related?"]
)

# ---------------- TAB 1: FAMILY TREE ----------------
with tab_tree:
    tree = Digraph("FamilyTree")
    tree.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.6",
        ranksep="1.2"
    )

    edges = [
        (u, v, a["type"])
        for u, v, a in graph.edges(data=True)
        if a.get("type") in SAFE_RELATIONS
    ]

    if len(edges) > MAX_EDGES:
        st.warning(
            f"Tree is large ({len(edges)} relations). "
            f"Showing first {MAX_EDGES}."
        )
        edges = edges[:MAX_EDGES]

    # Nodes
    for node in graph.nodes():
        tree.node(
            node,
            node,
            shape="box",
            style="rounded",
            fontsize="10"
        )

    # Edges with relation labels
    for i, (u, v, rel) in enumerate(edges):
        rel_node = f"rel_{i}"
        tree.node(
            rel_node,
            rel,
            shape="box",
            style="rounded,filled",
            fillcolor="#f3f4f6",
            fontsize="9",
            width="1.2",
            height="0.35"
        )
        tree.edge(u, rel_node)
        tree.edge(rel_node, v)

    # IMPORTANT: no fixed-height wrapper → no gap
    st.graphviz_chart(tree, use_container_width=True)

# ---------------- TAB 2: RELATION SEARCH ----------------
with tab_relation:
    if not search_clicked:
        st.info("Enter two names and click Search.")
    else:
        a = normalize(person_a_input)
        b = normalize(person_b_input)

        if not a or not b:
            st.error("One or both names not found.")
        else:
            try:
                path = nx.shortest_path(
                    graph.to_undirected(),
                    a,
                    b
                )

                st.success("Relationship Explanation")

                for i in range(len(path) - 1):
                    x, y = path[i], path[i + 1]
                    if graph.has_edge(x, y):
                        rel = graph[x][y]["type"]
                        st.markdown(
                            f"**{x}** is the **{rel}** of **{y}**"
                        )
                    else:
                        st.markdown(
                            f"**{x}** is related to **{y}**"
                        )

            except nx.NetworkXNoPath:
                st.error("No relationship path found.")
