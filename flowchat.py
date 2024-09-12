import ast

class FlowchartGenerator(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        self.current_node_id = None

    def add_node(self, text, shape="rectangle"):
        node_id = f"node{self.node_counter}"
        self.node_counter += 1
        self.nodes.append({
            "id": node_id,
            "text": text,
            "shape": shape,
            "x": 100,
            "y": 100 + self.node_counter * 100
        })
        return node_id

    def add_edge(self, source, target):
        self.edges.append({
            "source": source,
            "target": target
        })

    def visit_FunctionDef(self, node):
        func_node_id = self.add_node(f"Function: {node.name}", shape="ellipse")
        if self.current_node_id:
            self.add_edge(self.current_node_id, func_node_id)
        self.current_node_id = func_node_id
        self.generic_visit(node)

    def visit_If(self, node):
        if_node_id = self.add_node("If Condition")
        self.add_edge(self.current_node_id, if_node_id)
        self.current_node_id = if_node_id
        self.generic_visit(node)

    def visit_For(self, node):
        for_node_id = self.add_node("For Loop")
        self.add_edge(self.current_node_id, for_node_id)
        self.current_node_id = for_node_id
        self.generic_visit(node)

    # Add more visit methods for different node types...

    def generate_drawio_xml(self):
        xml_parts = []

        # Define the start of the XML diagram
        xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_parts.append('<mxfile host="app.diagrams.net">')
        xml_parts.append('<diagram name="Page-1">')
        xml_parts.append('<mxGraphModel>')
        xml_parts.append('<root>')
        xml_parts.append('<mxCell id="0" />')
        xml_parts.append('<mxCell id="1" parent="0" />')

        # Add each node to the XML
        for node in self.nodes:
            xml_parts.append(f'''
                <mxCell id="{node['id']}" value="{node['text']}" style="shape={node['shape']};" vertex="1" parent="1">
                    <mxGeometry x="{node['x']}" y="{node['y']}" width="120" height="60" as="geometry" />
                </mxCell>
            ''')

        # Add each edge to the XML
        for edge in self.edges:
            xml_parts.append(f'''
                <mxCell edge="1" source="{edge['source']}" target="{edge['target']}" parent="1">
                    <mxGeometry relative="1" as="geometry" />
                </mxCell>
            ''')

        # Close the XML tags
        xml_parts.append('</root>')
        xml_parts.append('</mxGraphModel>')
        xml_parts.append('</diagram>')
        xml_parts.append('</mxfile>')

        return ''.join(xml_parts)

def generate_flowchart_from_code(code):
    tree = ast.parse(code)
    generator = FlowchartGenerator()
    generator.visit(tree)
    return generator.generate_drawio_xml()

# Example usage
if __name__ == "__main__":
    code = """
def process_data(data):
    try:
        result = []
        for item in data:
            if isinstance(item, int):
                if item % 2 == 0:
                    result.append(item * 2)
                else:
                    result.append(item * 3)
            elif isinstance(item, str):
                result.append(item.upper())
            else:
                result.append(None)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
"""
    xml_output = generate_flowchart_from_code(code)
    with open("flowchart.xml", "w") as file:
        file.write(xml_output)
    print("Flowchart XML has been generated and saved to flowchart.xml")
