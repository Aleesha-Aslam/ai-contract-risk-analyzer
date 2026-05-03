import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

def build_entity_graph(entities, bg_color="#0f1117"):
    net = Network(
        height="500px",
        width="100%",
        bgcolor=bg_color,
        font_color="#e6edf3",
        directed=True
    )

    net.set_options("""
    {
        "nodes": {
            "shape": "dot",
            "scaling": { "min": 20, "max": 40 },
            "font": { "size": 14, "face": "Arial" }
        },
        "edges": {
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } },
            "smooth": { "type": "curvedCW", "roundness": 0.2 },
            "width": 2
        },
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 120
            },
            "solver": "forceAtlas2Based",
            "stabilization": { "iterations": 150 }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)

    color_map = {
        "👤 People / Parties":  {"color": "#6366f1", "size": 30},
        "🏢 Organizations":     {"color": "#06b6d4", "size": 35},
        "📅 Dates & Deadlines": {"color": "#f59e0b", "size": 20},
        "💰 Money & Amounts":   {"color": "#22c55e", "size": 22},
        "📍 Locations":         {"color": "#f85149", "size": 25},
        "⚖️ Legal References":  {"color": "#8b5cf6", "size": 20},
    }

    added_nodes = set()

    orgs = entities.get("🏢 Organizations", [])
    for org in orgs:
        if org not in added_nodes:
            net.add_node(
                org, label=org,
                color=color_map["🏢 Organizations"]["color"],
                size=color_map["🏢 Organizations"]["size"],
                title=f"🏢 Organization: {org}"
            )
            added_nodes.add(org)

    for label, items in entities.items():
        if label == "🏢 Organizations":
            continue
        cfg = color_map.get(label, {"color": "#8b949e", "size": 18})
        for item in items:
            if item not in added_nodes:
                net.add_node(
                    item, label=item,
                    color=cfg["color"],
                    size=cfg["size"],
                    title=f"{label}: {item}"
                )
                added_nodes.add(item)
            if orgs:
                for org in orgs[:2]:
                    if item != org:
                        net.add_edge(org, item, color="#30363d", width=1.5)

    people = entities.get("👤 People / Parties", [])
    for person in people:
        for org in orgs:
            if person != org and person in added_nodes and org in added_nodes:
                net.add_edge(person, org, color="#6366f1", width=2.5, title=f"{person} → {org}")

    locations = entities.get("📍 Locations", [])
    for loc in locations:
        for org in orgs:
            if loc in added_nodes and org in added_nodes:
                net.add_edge(org, loc, color="#f85149", width=1.5, title=f"{org} → {loc}")

    # ✅ Windows fix — write to file without deleting
    tmpfile = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode="w",
        encoding="utf-8"
    )
    tmpfile.close()  # ← close first before pyvis writes to it
    net.save_graph(tmpfile.name)

    with open(tmpfile.name, "r", encoding="utf-8") as f:
        html = f.read()

    # ✅ Safe delete after reading
    try:
        os.unlink(tmpfile.name)
    except Exception:
        pass  # ignore if Windows still locks it

    return html