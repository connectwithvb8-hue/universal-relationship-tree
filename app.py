import streamlit as st
from graphviz import Digraph

from loaders import load_json, load_csv
from graph_builder import build_graph
from relation_styles import RELATION_STYLES


# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="Universal Relationship Tree",
    layout="wide"
)

st.title("Universal Relationship Tree Generator")
st.caption(
    "Upload a JSON or CSV file to visualize family and social relationships "
    "(family, friends, spouse, adoptive relations, etc.)"
)


# -------------------------
# File upload
# -------------------------
uploaded_file = st.file_uploader(
    "Upload character data (JSON or CSV)",
    type=["json", "csv"]
)


# -------------------------
# Graph rendering
# -------------------------
if uploaded_file:

    # Load data based on file type
    if uploaded_file.name.lower().endswith(".json"):
        data = load_json(uploaded_file)
    else:
        data = load_csv(uploaded_file)

    # Build graph
    graph = build_graph(data)

    # Create Graphviz diagram
    dot = Digraph(engine="dot")
    dot.attr(rankdir="TB", fontsize="10")

    # -------------------------
    # Draw nodes
    # -------------------------
    for node, attrs in graph.nodes(data=True):
        group = attrs.get("group", "Unknown")

        # Color nodes by group (optional logic)
        fillcolor = "lightgray"
        if group.lower() == "nielsen":
            fillcolor = "lightblue"
        elif group.lower() == "kahnwald":
            fillcolor = "lightgreen"
        elif group.lower() == "doppler":
            fillcolor = "lightcoral"

        dot.node(
            node,
            node,
            style="filled",
            fillcolor=fillcolor
        )

    # -------------------------
    # Draw edges
    # -------------------------
    for u, v, attrs in graph.edges(data=True):
        relation_type = attrs.get("type", "relation")
        style = RELATION_STYLES.get(relation_type, {})

        dot.edge(
            u,
            v,
            label=relation_type,
            color=style.get("color", "black"),
            style=style.get("style", "solid")
        )

    # Render graph
    st.graphviz_chart(dot)

else:
    st.info(
        "Upload a JSON or CSV file to generate the relationship tree.\n\n"
        "CSV format example:\n"
        "character,relationship,relative,group"
    )
