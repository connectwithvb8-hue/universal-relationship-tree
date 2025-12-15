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

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Relation Fandom",
    page_icon="🌳",
    layout="wide"
)

# ---------------- HARD RESET STREAMLIT SPACING ----------------
st.markdown(
    """
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }

        section.main > div {
            padding-top: 0rem !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0rem !important;
        }

        .stTabs {
            margin-top: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
st.markdown(
    "<h2 style='margin-bottom:0.3rem;'>🌳 Relation Fandom</h2>",
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload CSV or JSON",
        type=["csv", "json"]
    )
    person_a_input = st.text_input("Person A")
    person_b_input = st.text_input("Person B")
    search_clicked = st.button("Search Relationship")

# ---------------- LOAD DATA ----------------
if not uploaded_file:
    st.stop()

if uploaded_file.name.lower().endswith(".json"):
    data = load_json(uploaded_file)
else:
    data = load_csv(uploaded_file)

graph = build_graph(data)

# ---------------- HELPERS ----------------
name_lookup = {n.lower(): n for n in graph.nodes()}

def normalize(name):
    if not name:
        return None
    return name_lookup.get(name.strip().lower())

# ---------------- TABS ----------------
tab_tree, tab_relation = st.tabs(
    ["Family Tree", "How Are They Related?"]
)

# ---------------- TAB 1: TREE ----------------
with tab_tree:
    tree = Digraph("FamilyTree")
    tree.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.6",
        ranksep="1.2",
        size="8,12!"
    )

    edges = [
        (u, v, a["type"])
        for u, v, a in graph.edges(data=True)
        if a.get("type") in SAFE_RELATIONS
    ][:MAX_EDGES]

    for node in graph.nodes():
        tree.node(
            node,
            node,
            shape="box",
            style="rounded",
            fontsize="10"
        )

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

    st.markdown(
        "<div style='height:82vh; overflow:auto;'>",
        unsafe_allow_html=True
    )
    st.graphviz_chart(tree, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 2: RELATION SEARCH ----------------
with tab_relation:
    if search_clicked:
        a = normalize(person_a_input)
        b = normalize(person_b_input)

        if a and b:
            try:
                path = nx.shortest_path(graph.to_undirected(), a, b)
                for i in range(len(path) - 1):
                    x, y = path[i], path[i + 1]
                    if graph.has_edge(x, y):
                        st.write(
                            f"{x} → {graph[x][y]['type']} → {y}"
                        )
            except nx.NetworkXNoPath:
                st.write("No relationship found.")
