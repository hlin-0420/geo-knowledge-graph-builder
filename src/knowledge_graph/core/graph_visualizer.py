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
            print(f"Record: {record}")
            filtered_src = {k: record[k] for k in ['t', 'n'] if k in record}
            print(f"Filtered node: {filtered_src}")
            if 't' in filtered_src:
                record_key = 't'
            else:
                record_key = 'n'
                
            
            node_attributes = {k: v for k, v in record.items() if k != record_key}
            net.add_node(record_key, **node_attributes)
        
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