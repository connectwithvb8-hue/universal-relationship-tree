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

st.set_page_config(
    page_title="Relation Fandom",
    page_icon="🌳",
    layout="wide"
)

st.title("🌳 Relation Fandom")
st.caption(
    "Optimized for stability. Scroll to explore the tree. "
    "Use browser zoom on mobile if needed."
)

@st.cache_data(show_spinner=False)
def load_data(file):
    if file.name.lower().endswith(".json"):
        return load_json(file)
    return load_csv(file)

@st.cache_data(show_spinner=False)
def build_cached_graph(data):
    return build_graph(data)

@st.cache_data(show_spinner=False)
def build_tree_source(graph):
    tree = Digraph("FamilyTree")
    tree.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.6",
        ranksep="1.2",
        size="8,12!"  # Important: bigger SVG → smoother zoom
    )

    safe_edges = [
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

    for i, (u, v, rel) in enumerate(safe_edges):
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

    return tree

with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    person_a_input = st.text_input("Person A")
    person_b_input = st.text_input("Person B")
    search_clicked = st.button("Search Relationship")

if not uploaded_file:
    st.info("Upload a file to continue.")
    st.stop()

data = load_data(uploaded_file)
graph = build_cached_graph(data)

name_lookup = {n.lower(): n for n in graph.nodes()}
def normalize(name):
    return name_lookup.get(name.strip().lower()) if name else None

tab_tree, tab_relation = st.tabs(["Family Tree", "How Are They Related?"])

with tab_tree:
    st.info(
        "Tip: Scroll to explore. On mobile, use browser zoom "
        "(two-finger zoom in browser menu)."
    )

    tree = build_tree_source(graph)

    # Scrollable container → smoother on mobile & PC
    st.markdown(
        "<div style='height:85vh; overflow:auto;'>",
        unsafe_allow_html=True
    )
    st.graphviz_chart(tree, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab_relation:
    if not search_clicked:
        st.info("Enter two names and click Search.")
    else:
        a = normalize(person_a_input)
        b = normalize(person_b_input)

        if not a or not b:
            st.error("Names not found.")
        else:
            try:
                path = nx.shortest_path(graph.to_undirected(), a, b)
                st.success("Relationship Explanation")

                for i in range(len(path) - 1):
                    x, y = path[i], path[i + 1]
                    if graph.has_edge(x, y):
                        rel = graph[x][y]["type"]
                        st.markdown(f"**{x}** is the **{rel}** of **{y}**")
                    else:
                        st.markdown(f"**{x}** is related to **{y}**")

            except nx.NetworkXNoPath:
                st.error("No relationship path found.")
