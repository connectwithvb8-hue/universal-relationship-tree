import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from loaders import load_json, load_csv
from graph_builder import build_graph
from relation_styles import RELATION_STYLES



st.set_page_config(
    page_title="Relationship Intelligence Platform",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Relationship Intelligence Platform")
st.markdown(
    """
    A professional, interactive tool to visualize **family and social relationships**
    for books, web series, movies, or custom datasets.

    • Upload CSV or JSON  
    • Zoom, pan, and drag nodes  
    • Mobile & desktop friendly  
    """
)



with st.sidebar:
    st.header("📤 Upload Data")

    uploaded_file = st.file_uploader(
        "Upload CSV or JSON file",
        type=["csv", "json"]
    )

    st.markdown("---")
    st.caption(
        "📱 Mobile: pinch to zoom • drag to move\n\n"
        "🖥 Desktop: scroll to zoom • drag to pan"
    )

    st.markdown("---")
    st.caption(
        "**Relations**\n"
        "- Solid → Family\n"
        "- Dashed → Friend\n"
        "- Dotted → Enemy"
    )



if not uploaded_file:
    st.info("👈 Upload a CSV or JSON file from the sidebar to get started.")
    st.stop()



if uploaded_file.name.lower().endswith(".json"):
    data = load_json(uploaded_file)
else:
    data = load_csv(uploaded_file)

graph = build_graph(data)



net = Network(
    height="600px",          # Mobile + desktop safe height
    width="100%",
    bgcolor="#ffffff",
    font_color="#1f2937",
    directed=True
)

net.toggle_physics(True)



for node, attrs in graph.nodes(data=True):
    net.add_node(
        node,
        label=node,
        title=f"<b>{node}</b>",
        shape="dot",
        size=18
    )



for u, v, attrs in graph.edges(data=True):
    rel = attrs.get("type", "relation")
    style = RELATION_STYLES.get(rel, {})

    net.add_edge(
        u,
        v,
        label=rel,
        color=style.get("color", "#6b7280"),
        dashes=(style.get("style") == "dashed")
    )



net.set_options("""
var options = {
  interaction: {
    hover: true,
    dragNodes: true,
    dragView: true,
    zoomView: true,
    navigationButtons: true,
    keyboard: false
  },
  physics: {
    enabled: true,
    stabilization: {
      iterations: 200
    },
    barnesHut: {
      gravitationalConstant: -20000,
      springLength: 120,
      springConstant: 0.04
    }
  }
}
""")



html = net.generate_html()
components.html(html, height=650, scrolling=True)
