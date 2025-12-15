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
    "adoptive son", "adoptive daughter"
}

MAX_EDGES = 500

st.set_page_config(
    page_title="Relation Fandom",
    page_icon="🌳",
    layout="wide"
)

st.title("🌳 Relation Fandom")
st.markdown(
    "A mobile-friendly family tree with smooth zooming and clear relationship labels."
)

with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    person_a_input = st.text_input("Person A")
    person_b_input = st.text_input("Person B")
    search_clicked = st.button("Search Relationship")

if not uploaded_file:
    st.info("Upload a CSV or JSON file to continue.")
    st.stop()

data = load_json(uploaded_file) if uploaded_file.name.endswith(".json") else load_csv(uploaded_file)
graph = build_graph(data)

name_lookup = {n.lower(): n for n in graph.nodes()}
normalize = lambda n: name_lookup.get(n.strip().lower()) if n else None

tab_tree, tab_relation = st.tabs(["Family Tree", "How Are They Related?"])

with tab_tree:
    st.info("Use pinch-to-zoom on mobile or Ctrl + scroll on desktop.")

    tree = Digraph("FamilyTree", format="svg")
    tree.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.5",
        ranksep="1.2"
    )

    safe_edges = [
        (u, v, a["type"])
        for u, v, a in graph.edges(data=True)
        if a.get("type") in SAFE_RELATIONS
    ][:MAX_EDGES]

    for node in graph.nodes():
        tree.node(node, node, shape="box", style="rounded", fontsize="10")

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

    svg = tree.pipe(format="svg").decode("utf-8")

    st.components.v1.html(
        f"""
        <div style="
            width:100%;
            height:80vh;
            overflow:auto;
            touch-action: pan-x pan-y pinch-zoom;
            background-color: #0e1117;
        ">
            <div style="
                transform-origin: 0 0;
            ">
                {svg}
            </div>
        </div>
        """,
        height=800,
        scrolling=True
    )

with tab_relation:
    if not search_clicked:
        st.info("Enter two names and click Search.")
    else:
        a, b = normalize(person_a_input), normalize(person_b_input)
        if not a or not b:
            st.error("Names not found.")
        else:
            try:
                path = nx.shortest_path(graph.to_undirected(), a, b)
                st.success("Relationship Explanation")
                for i in range(len(path) - 1):
                    x, y = path[i], path[i + 1]
                    if graph.has_edge(x, y):
                        st.markdown(f"**{x}** is the **{graph[x][y]['type']}** of **{y}**")
                    else:
                        st.markdown(f"**{x}** is related to **{y}**")
            except nx.NetworkXNoPath:
                st.error("No relationship path found.")
