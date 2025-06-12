from pyvis.network import Network
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Adds src/ to path

# Create output directory path relative to project root
output_dir = Path(__file__).resolve().parents[3] / "Output" / "Neo4j_Graph"
output_dir.mkdir(parents=True, exist_ok=True)

from qa_bot.core.graph import graph
from neo4j.graph import Node, Relationship


class GraphVisualizer:
    def __init__(self, neo4j_graph=None):
        self.graph = neo4j_graph or graph

    def visualize_subgraph(self, query, output_file):
        """Visualize a subgraph using PyVis"""
        query = query or """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """

        results = self.graph.query(query)
        net = Network(height="750px", width="100%", notebook=False, directed=True)
        seen_nodes = set()

        for record in results:
            node1 = record["n"]
            node2 = record["m"]
            rel = record["r"]

            # Fallback: use elementId or hash as ID since 'id' may not be present
            node1_id = node1.get("elementId") or str(hash(str(node1)))
            if node1_id not in seen_nodes:
                label1 = node1.get("name") or "Node"
                net.add_node(node1_id, label=label1, title=str(node1), shape="dot")
                seen_nodes.add(node1_id)

            node2_id = node2.get("elementId") or str(hash(str(node2)))
            if node2_id not in seen_nodes:
                label2 = node2.get("name") or "Node"
                net.add_node(node2_id, label=label2, title=str(node2), shape="dot")
                seen_nodes.add(node2_id)

            # Add edge
            try:
                rel_label = rel.get("type", "REL") if isinstance(rel, dict) else getattr(rel, "type", "REL")
                net.add_edge(node1_id, node2_id, label=rel_label, title=str(rel))
            except Exception as e:
                print(f"Error adding edge: {e}")

        net.write_html(output_file)
        print(f"Graph saved to {output_file}")
        return net


if __name__ == "__main__":
    viz = GraphVisualizer()

    # Visualize specific subgraph and save to that path
    viz.visualize_subgraph("""
        MATCH (n)-[r]->(m)
        RETURN n, r, m
    """, str(output_dir / "formats_graph.html"))