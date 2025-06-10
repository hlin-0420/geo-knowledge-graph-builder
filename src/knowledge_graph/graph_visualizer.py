from pyvis.network import Network
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Adds src/ to path
from qa_bot.graph import graph

class GraphVisualizer:
    def __init__(self, neo4j_graph=None):
        self.graph = neo4j_graph or graph
        
    def visualize_subgraph(self, query=None, output_file="knowledge_graph.html"):
        """Visualize a subgraph using PyVis"""
        # Default query shows nodes and relationships
        query = query or """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """
        
        results = self.graph.query(query)
        net = Network(height="750px", width="100%", notebook=False, directed=True)
        
        # Process nodes and edges
        seen_nodes = set()
        for record in results:
            # Add source node
            src = record['n']
            if src.id not in seen_nodes:
                net.add_node(src.id, label=next(iter(src.labels)), title=str(src))
                seen_nodes.add(src.id)
            
            # Add target node
            tgt = record['m']
            if tgt.id not in seen_nodes:
                net.add_node(tgt.id, label=next(iter(tgt.labels)), title=str(tgt))
                seen_nodes.add(tgt.id)
            
            # Add edge
            rel = record['r']
            net.add_edge(src.id, tgt.id, title=rel.type)
        
        # Customize visualization
        net.toggle_physics(True)
        net.show_buttons(filter_=['physics'])
        net.show(output_file)
        return net

def visualize_curve_types():
    """Specialized visualization for curve types"""
    viz = GraphVisualizer()
    return viz.visualize_subgraph("""
    MATCH (t:Type)-[r]->(x)
    WHERE t:Curve OR ANY(label IN labels(t) WHERE label CONTAINS 'Curve')
    RETURN t, r, x
    """, "curve_graph.html")
    
if __name__ == "__main__":
    viz = GraphVisualizer()
    
    # Visualize entire graph (sample)
    viz.visualize_subgraph()
    
    # Or visualize specific subgraph
    viz.visualize_subgraph("""
    MATCH (t:Type)-[:HAS_FORMAT]->(f:Format)
    RETURN t, f
    """, "formats_graph.html")