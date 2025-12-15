import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import os

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

MAX_EDGES = 800

st.set_page_config(
    page_title="Relation Fandom",
    page_icon="🌳",
    layout="wide"
)

st.title("🌳 Relation Fandom")
st.markdown(
    "An interactive, smooth, mobile-friendly relationship tree with zoom and pan."
)

@st.cache_data(show_spinner=False)
def load_data(file):
    if file.name.lower().endswith(".json"):
        return load_json(file)
    return load_csv(file)

@st.cache_data(show_spinner=False)
def build_cached_graph(data):
    return build_graph(data)

with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    person_a_input = st.text_input("Person A")
    person_b_input = st.text_input("Person B")
    search_clicked = st.button("Search Relationship")

if not uploaded_file:
    st.info("Upload a CSV or JSON file to continue.")
    st.stop()

data = load_data(uploaded_file)
graph = build_cached_graph(data)

name_lookup = {n.lower(): n for n in graph.nodes()}
def normalize(name):
    return name_lookup.get(name.strip().lower()) if name else None

tab_tree, tab_relation = st.tabs(["Family Tree", "How Are They Related?"])

with tab_tree:
    st.info("Pinch-to-zoom on mobile • Scroll / drag to pan • Double-click to reset view")

    net = Network(
        height="80vh",
        width="100%",
        bgcolor="#0e1117",
        font_color="white",
        directed=True
    )

    net.toggle_physics(False)

    for node in graph.nodes():
        net.add_node(
            node,
            label=node,
            shape="box",
            color="#1f2937"
        )

    count = 0
    for u, v, attrs in graph.edges(data=True):
        rel = attrs.get("type")
        if rel in SAFE_RELATIONS:
            net.add_edge(
                u,
                v,
                label=rel,
                arrows="to",
                font={"size": 12, "align": "middle"},
                color="#9ca3af"
            )
            count += 1
        if count >= MAX_EDGES:
            break

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        html_path = tmp.name

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=800, scrolling=True)

    os.unlink(html_path)

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
