import sys
import os
import inspect
from typing import Dict, List, Tuple, Set, Optional
import json
import time

class FunctionCallTracer:
    def __init__(self, output_dir: str = '.', include_stdlib: bool = False, max_depth: int = None):
        self.output_dir = output_dir
        self.include_stdlib = include_stdlib
        self.max_depth = max_depth  # Maximum call depth to trace
        self.call_graph = {}  # Store function calls and their relationships
        self.func_params = {}  # Store function parameters
        self.current_stack = []  # Track current call stack
        self.excluded_paths = set()  # Paths to exclude
        self.entry_point = None  # Track the first function called
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Find standard library paths to exclude
        if not include_stdlib:
            self.excluded_paths = self._get_stdlib_paths()
    
    def _get_stdlib_paths(self) -> Set[str]:
        """Get paths to standard library modules to exclude them from tracing."""
        paths = set()
        for module in sys.modules.values():
            if module and hasattr(module, '__file__') and module.__file__:
                if 'site-packages' not in module.__file__ and ('lib' in module.__file__ or 'dist-packages' in module.__file__):
                    paths.add(os.path.dirname(module.__file__))
        return paths
    
    def _should_trace(self, filename: str) -> bool:
        """Determine if a file should be traced."""
        if not filename or filename == '<string>':
            return False
            
        # Skip standard library
        if not self.include_stdlib:
            for excluded in self.excluded_paths:
                if excluded and filename.startswith(excluded):
                    return False
        
        # Skip other libraries in site-packages or dist-packages
        if 'site-packages' in filename or 'dist-packages' in filename:
            return False
        
        # Skip Python standard library
        if filename.startswith(sys.prefix):
            return False
        
        # Only trace files from the application path
        app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # If the file is in the application path or its subdirectories
        if filename.startswith(app_path):
            return True
        
        # Optionally, you can add more application paths to include
        # For example, the current working directory
        cwd = os.path.abspath(os.getcwd())
        if filename.startswith(cwd):
            return True
            
        # If none of the above, don't trace it
        return False
    
    def trace_calls(self, frame, event, arg):
        """Trace function calls."""
        if event != 'call':
            return self.trace_calls
            
        # Get function details
        func_filename = frame.f_code.co_filename
        if not self._should_trace(func_filename):
            return self.trace_calls
            
        func_name = frame.f_code.co_name
        line_no = frame.f_lineno
        
        # Check depth limit if specified
        if self.max_depth is not None and len(self.current_stack) >= self.max_depth:
            return self.trace_calls
        
        # Get calling function (parent)
        parent = None
        if self.current_stack:
            parent = self.current_stack[-1]
        
        # Create function identifier (full path for uniqueness)
        func_id = f"{func_filename}:{func_name}:{line_no}"
        
        # Store entry point
        if not self.entry_point and not parent:
            self.entry_point = func_id
        
        # Enhanced class method detection
        class_name = None
        is_mock = False
        
        # Check if this is a call to a mock object
        if 'self' in frame.f_locals:
            instance = frame.f_locals['self']
            
            # Check for mock objects
            mock_module_names = ['unittest.mock', 'mock']
            instance_module = getattr(instance.__class__, '__module__', '')
            
            if instance_module in mock_module_names or hasattr(instance, '_mock_name'):
                is_mock = True
                
                # Try to get the original function/method being mocked
                try:
                    if hasattr(instance, '_mock_wraps') and instance._mock_wraps:
                        # Get the original function if it's wrapped
                        original_func = instance._mock_wraps
                        if hasattr(original_func, '__self__'):
                            # It's a bound method
                            class_name = original_func.__self__.__class__.__name__
                            mocked_func_name = original_func.__name__
                            func_name = f"{class_name}.{mocked_func_name}"
                        else:
                            # It's a function
                            func_name = original_func.__name__
                        
                        # Update the identifier
                        func_id = f"{func_filename}:{func_name}:{line_no} (mocked)"
                    elif hasattr(instance, '_mock_name') and instance._mock_name:
                        # If wrapped function isn't available, use the mock name
                        if '.' in instance._mock_name:
                            func_name = instance._mock_name
                        else:
                            func_name = f"{func_name} ({instance._mock_name})"
                        func_id = f"{func_filename}:{func_name}:{line_no} (mocked)"
                except Exception:
                    # Fall back to standard handling if mock introspection fails
                    pass
            else:
                # Regular class method detection (not a mock)
                try:
                    # Get class name from self's class
                    class_name = instance.__class__.__name__
                    
                    # Create an identifier that includes class name
                    class_func_id = f"{func_filename}:{class_name}.{func_name}:{line_no}"
                    
                    # Replace the original ID with the class-aware ID
                    if parent and parent in self.call_graph:
                        # Update the parent's children list if needed
                        for i, child in enumerate(self.call_graph[parent]):
                            if child == func_id:
                                self.call_graph[parent][i] = class_func_id
                    
                    # Use the new ID for this function
                    func_id = class_func_id
                except (AttributeError, TypeError):
                    # In case self doesn't have a __class__ attribute or other issues
                    pass
        
        # Special handling for __init__ to associate it with the class
        elif func_name == "__init__":
            # Try to find the class name by inspecting the code
            try:
                # Get the class name from the code context
                if hasattr(frame, 'f_back') and frame.f_back:
                    back_code = frame.f_back.f_code
                    if back_code.co_name in ('__new__', 'type', '_call_'):
                        for key, val in frame.f_back.f_locals.items():
                            if isinstance(val, type) and val.__name__ not in ('type', 'object'):
                                class_name = val.__name__
                                class_func_id = f"{func_filename}:{class_name}.{func_name}:{line_no}"
                                func_id = class_func_id
                                break
            except Exception:
                # Fall back to standard handling if we can't identify the class
                pass
        
        # Store relationship
        if parent:
            if parent not in self.call_graph:
                self.call_graph[parent] = []
            if func_id not in self.call_graph[parent]:
                self.call_graph[parent].append(func_id)
        
        # Store function details (parameters)
        locals_dict = frame.f_locals.copy()  # Make a copy to avoid reference issues
        
        # Handle mock object side effects
        if is_mock and 'self' in locals_dict:
            instance = locals_dict['self']
            if hasattr(instance, 'side_effect') and callable(instance.side_effect):
                # Track the side_effect function as well
                side_effect_func = instance.side_effect
                if hasattr(side_effect_func, '__name__'):
                    locals_dict['__side_effect__'] = side_effect_func.__name__
        
        # Store parameters (excluding self)
        params = {name: (repr(val), type(val).__name__) 
                for name, val in locals_dict.items()
                if name != 'self'}  # Skip 'self' for class methods
        
        # Store class info in the parameters if available
        if class_name:
            params['__class_name__'] = (class_name, 'class')
        
        # Store mock info if available
        if is_mock:
            params['__is_mock__'] = ('True', 'bool')
        
        self.func_params[func_id] = params
        
        # Update stack
        self.current_stack.append(func_id)
        
        return self.trace_calls
    def trace_returns(self, frame, event, arg):
        """Trace function returns to maintain the stack."""
        if event == 'return' and self.current_stack:
            self.current_stack.pop()
        return self.trace_returns
    
    def start_tracing(self):
        """Start tracing function calls."""
        sys.settrace(self.trace_calls)
    
    def stop_tracing(self):
        """Stop tracing function calls."""
        sys.settrace(None)
    
    def generate_mermaid_diagram(self, filename: str = 'function_calls.md'):
        """Generate a Mermaid.js flowchart diagram of the function calls."""
        full_path = os.path.join(self.output_dir, filename)
        
        with open(full_path, 'w') as f:
            f.write("# Function Call Diagram\n\n")
            f.write("```mermaid\nflowchart TD\n")
            
            # Create nodes for each function
            nodes = set()
            for parent in self.call_graph:
                nodes.add(parent)
                for child in self.call_graph[parent]:
                    nodes.add(child)
            
            # Generate clean node IDs to avoid syntax issues
            node_ids = {}
            for i, node in enumerate(nodes):
                # Create a short, clean ID for each node
                file, func, line = node.split(':', 2)
                clean_func = func.replace('__', '')
                node_ids[node] = f"func{i}_{clean_func}"
            
            # Write node definitions with parameters
            for node in nodes:
                file, func, line = node.split(':', 2)
                node_id = node_ids[node]
                
                # Clean up function name for display
                display_func = func
                
                # Format parameters nicely
                param_text = ""
                if node in self.func_params and self.func_params[node]:
                    params = []
                    for name, (value, type_name) in self.func_params[node].items():
                        # # Truncate long values
                        # if len(value) > 15:
                        #     value = value[:12] + "..."
                        params.append(f"{name}: {value} ({type_name})")
                    
                    # Format parameters in a readable way
                    if params:
                        param_text = "<br>" + "<br>".join(params)
                
                # Write node with function name and parameters
                label = f"{func}(){param_text}"
                if func != "__init__":  # Add filename for non-constructor methods
                    label = f"{os.path.basename(file)}<br>{label}"
                    
                f.write(f'    {node_id}["{label}"]\n')
            
            # Write edges
            for parent in self.call_graph:
                parent_id = node_ids[parent]
                for child in self.call_graph[parent]:
                    child_id = node_ids[child]
                    f.write(f"    {parent_id} --> {child_id}\n")
            
            # Add better styling
            f.write("\n    %% Styling\n")
            f.write("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px\n")
            f.write("    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px\n")
            f.write("    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px\n")
            f.write("    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px\n")
            f.write("    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px\n")
            
            # Apply styles based on function name patterns
            for node in nodes:
                file, func, line = node.split(':', 2)
                node_id = node_ids[node]
                
                if func == "main" or func.startswith("main_"):
                    f.write(f"    class {node_id} mainMethod\n")
                elif func == "__init__":
                    f.write(f"    class {node_id} initMethod\n")
                elif func.startswith("__") or '_' in func and not func.startswith("_"):
                    f.write(f"    class {node_id} privateMethod\n")
                else:
                    f.write(f"    class {node_id} utilMethod\n")
            
            f.write("```\n")
        
        print(f"Mermaid diagram generated: {full_path}")
        return full_path
    
    def generate_html_visualization(self, filename: str = 'function_calls.html'):
        """Generate an interactive HTML visualization."""
        return FunctionVisualizer.generate_html(self, filename)


class FunctionVisualizer:
    """Creates interactive HTML visualizations from function call data."""
    
    @staticmethod
    def generate_html(tracer, filename='function_calls.html'):
        """Generate an interactive HTML visualization from tracer data."""
        output_path = os.path.join(tracer.output_dir, filename)
        
        # Prepare data for D3.js visualization
        nodes = []
        links = []
        node_map = {}  # Map function IDs to node indices
        
        # First, collect all unique nodes and organize by classes
        all_nodes = set()
        classes = {}   # Store class nodes and their methods
        
        # Collect all nodes
        for parent in tracer.call_graph:
            all_nodes.add(parent)
            for child in tracer.call_graph[parent]:
                all_nodes.add(child)
                
        # Identify and organize class methods
        for node_id in all_nodes:
            parts = node_id.split(':')
            filepath = ':'.join(parts[:-2])
            func_name = parts[-2]
            
            # If it's a class method (contains a dot)
            if '.' in func_name:
                class_name, method_name = func_name.split('.', 1)
                
                # Create or update class entry
                if class_name not in classes:
                    classes[class_name] = {
                        'filepath': filepath,
                        'methods': []
                    }
                
                # Add this method to the class
                classes[class_name]['methods'].append(node_id)
        
        # First add class container nodes
        node_index = 0
        class_nodes = {}
        
        for class_name, class_info in classes.items():
            filepath = class_info['filepath']
            filename = os.path.basename(filepath)
            
            # Create a class container node
            class_node = {
                "id": node_index,
                "name": class_name,
                "filename": filename,
                "filepath": filepath,
                "line": "N/A",  # Classes span multiple lines
                "type": "class_container",
                "params": [],
                "methods": [],  # Will store indices of method nodes
                "collapsed": True  # Initially collapsed
            }
            
            nodes.append(class_node)
            class_nodes[class_name] = node_index
            node_index += 1
        
        # Now add all other nodes
        for node_id in all_nodes:
            # Extract file, function name, and line number
            parts = node_id.split(':')
            filepath = ':'.join(parts[:-2])
            func_name = parts[-2]
            line_no = parts[-1]
            
            # Get shortened filename for display
            filename = os.path.basename(filepath)
            
            # Check node type and handle class methods specially
            if '.' in func_name:
                class_name, method_name = func_name.split('.', 1)
                display_name = method_name  # Just show method name since it's grouped under class
                parent_class = class_name
                
                # Determine method type
                if method_name == "__init__":
                    node_type = "constructor"
                elif method_name.startswith("__"):
                    node_type = "private_method"
                else:
                    node_type = "class_method"
            elif func_name == "__init__":
                display_name = "__init__"
                node_type = "constructor"
                parent_class = None
            elif func_name.startswith("__"):
                display_name = func_name
                node_type = "private_method"
                parent_class = None
            elif func_name == "main" or func_name.startswith("main_"):
                display_name = func_name
                node_type = "main_method"
                parent_class = None
            else:
                display_name = func_name
                node_type = "function"
                parent_class = None
            
            # Format parameters
            params = []
            if node_id in tracer.func_params:
                for name, (value, type_name) in tracer.func_params[node_id].items():
                    # Truncate long values
                    # if len(value) > 20:
                    #     value = value[:17] + "..."
                    params.append({"name": name, "value": value, "type": type_name})
            
            # Skip if this is a class method (we'll handle these differently)
            if parent_class:
                # Store which methods belong to which class
                class_node_idx = class_nodes[parent_class]
                nodes[class_node_idx]["methods"].append(node_index)
            
            # Create node
            node = {
                "id": node_index,
                "name": display_name,
                "filename": filename,
                "filepath": filepath,
                "line": line_no,
                "type": node_type,
                "params": params,
                "parent_class": parent_class  # Reference to parent class if applicable
            }
            
            nodes.append(node)
            node_map[node_id] = node_index
            node_index += 1
        
        # Create links between nodes
        for parent in tracer.call_graph:
            for child in tracer.call_graph[parent]:
                if parent in node_map and child in node_map:
                    links.append({
                        "source": node_map[parent],
                        "target": node_map[child]
                    })
        
        # Prepare JSON data for D3
        graph_data = {
            "nodes": nodes,
            "links": links
        }
        
        # Generate HTML with embedded D3.js visualization
        with open(output_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Function Call Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        #graph {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .tooltip {
            position: absolute;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            max-width: 300px;
        }
        .param-name {
            font-weight: bold;
            color: #444;
        }
        .param-value {
            color: #0066cc;
        }
        .param-type {
            color: #666;
            font-style: italic;
        }
        .node circle {
            stroke-width: 2px;
        }
        .node text {
            font-size: 12px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }
        .controls {
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .controls button {
            background-color: #4285f4;
            color: white;
            border: none;
            padding: 8px 12px;
            margin-right: 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .controls button:hover {
            background-color: #3367d6;
        }
        #expandAllBtn {
            background-color: #34a853;
        }
        #expandAllBtn:hover {
            background-color: #2d8e47;
        }
        #collapseAllBtn {
            background-color: #fbbc05;
            color: #333;
        }
        #collapseAllBtn:hover {
            background-color: #f5ae00;
        }
        .legend {
            display: flex;
            justify-content: center;
            margin-top: 10px;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 0 10px;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            margin-right: 5px;
        }
        .legend-color.circle {
            border-radius: 50%;
        }
        .legend-color.square {
            border-radius: 3px;
        }
        
        /* Nodes and collapsing styles */
        .node[data-collapsed="true"] .expand-icon {
            cursor: pointer;
        }
        .node[data-collapsed="false"] .expand-icon {
            cursor: pointer;
        }
        .function-details {
            margin-top: 20px;
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Function Call Visualization</h1>
        
        <div class="controls">
            <div>
                <button id="resetBtn">Reset View</button>
                <button id="expandAllBtn">Expand All Classes</button>
                <button id="collapseAllBtn">Collapse All Classes</button>
            </div>
            <div>
                <label for="searchInput">Search: </label>
                <input type="text" id="searchInput" placeholder="Function name...">
            </div>
        </div>
        
        <div id="graph"></div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color square" style="background-color: #673ab7;"></div>
                <span>Classes (click to expand/collapse)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color circle" style="background-color: #4285f4;"></div>
                <span>Main Methods</span>
            </div>
            <div class="legend-item">
                <div class="legend-color circle" style="background-color: #34a853;"></div>
                <span>Regular Functions</span>
            </div>
            <div class="legend-item">
                <div class="legend-color circle" style="background-color: #fbbc05;"></div>
                <span>Private Methods</span>
            </div>
            <div class="legend-item">
                <div class="legend-color circle" style="background-color: #ea4335;"></div>
                <span>Constructors</span>
            </div>
            <div class="legend-item">
                <div class="legend-color circle" style="background-color: #9334e6;"></div>
                <span>Class Methods</span>
            </div>
        </div>
        
        <div id="functionDetails" class="function-details">
            <h3 id="selectedFunction">Function Details</h3>
            <p id="fileInfo">File: </p>
            <h4>Parameters:</h4>
            <table id="paramsTable">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Value</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>

    <script>
        // Graph data from Python
        const graphData = ''' + json.dumps(graph_data) + ''';
        
        // Color mapping by node type
        const colorMap = {
            main_method: "#4285f4",
            function: "#34a853", 
            private_method: "#fbbc05",
            constructor: "#ea4335",
            class_method: "#9334e6",
            class_container: "#673ab7"
        };
        
        // Set up the SVG
        const width = document.getElementById("graph").clientWidth;
        const height = 600;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .call(d3.zoom().on("zoom", (event) => {
                g.attr("transform", event.transform);
            }));
            
        const g = svg.append("g");
        
        // Set up the simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(50));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter()
            .append("line")
            .attr("class", "link")
            .attr("marker-end", "url(#arrowhead)");
        
        // Create arrowhead marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
        
        // Create nodes with proper formatting
        const node = g.append("g")
            .selectAll(".node")
            .data(graphData.nodes)
            .enter()
            .append("g")
            .attr("class", d => `node ${d.type}`)
            .attr("data-collapsed", d => d.collapsed)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("click", handleNodeClick);
        
        // Add appropriate shape to nodes
        node.each(function(d) {
            const nodeElement = d3.select(this);
            
            if (d.type === "class_container") {
                // Use rectangles for class containers
                nodeElement.append("rect")
                    .attr("width", 20)
                    .attr("height", 20)
                    .attr("rx", 4)
                    .attr("ry", 4)
                    .attr("x", -10)
                    .attr("y", -10)
                    .attr("fill", colorMap[d.type])
                    .attr("stroke", d3.rgb(colorMap[d.type]).darker(0.5))
                    .attr("stroke-width", 2);
                
                // Add a + symbol for collapsed class
                nodeElement.append("text")
                    .attr("class", "expand-icon")
                    .attr("text-anchor", "middle")
                    .attr("dominant-baseline", "central")
                    .attr("font-size", 12)
                    .attr("font-weight", "bold")
                    .attr("fill", "white")
                    .text("+");
            } else {
                // Use circles for functions and methods
                nodeElement.append("circle")
                    .attr("r", 10)
                    .attr("fill", d => colorMap[d.type])
                    .attr("stroke", d => d3.rgb(colorMap[d.type]).darker(0.5))
                    .attr("stroke-width", 2);
            }
        });
        
        // Add labels to nodes
        node.append("text")
            .attr("dx", 15)
            .attr("dy", 5)
            .text(d => {
                if (d.type === "class_container") {
                    return `Class ${d.name}`;
                } else if (d.parent_class) {
                    // For class methods, show ClassName.MethodName format
                    return `${d.parent_class}.${d.name}()`;
                } else {
                    return d.name + "()";
                }
            });
            
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        // Initialize visibility
        initializeVisibility();
        
        node.on("mouseover", function(event, d) {
            // Show tooltip
            tooltip.transition().duration(200).style("opacity", .9);
            
            // Create tooltip content
            let tooltipContent = "";
            if (d.type === "class_container") {
                tooltipContent = `<strong>Class ${d.name}</strong><br/>`;
            } else if (d.parent_class) {
                tooltipContent = `<strong>${d.parent_class}.${d.name}()</strong><br/>`;
            } else {
                tooltipContent = `<strong>${d.name}()</strong><br/>`;
            }
            
            if (d.params.length > 0) {
                tooltipContent += `<strong>Parameters:</strong><br/>`;
                d.params.forEach(param => {
                    tooltipContent += `<span class="param-name">${param.name}</span>: `;
                    tooltipContent += `<span class="param-value">${param.value}</span> `;
                    tooltipContent += `<span class="param-type">(${param.type})</span><br/>`;
                });
            } else {
                tooltipContent += "No parameters";
            }
            
            tooltip.html(tooltipContent)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            tooltip.transition().duration(500).style("opacity", 0);
        });
        
        // Function to update simulation
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Handle node clicks
        function handleNodeClick(event, d) {
            if (d.type === "class_container") {
                // Toggle class expansion/collapse
                toggleClassNode(d);
            } else {
                // Show function details for regular nodes
                showFunctionDetails(event, d);
            }
        }
        
        // Toggle class expansion/collapse
        function toggleClassNode(classNode) {
            // Toggle collapsed state
            classNode.collapsed = !classNode.collapsed;
            
            // Update the visual icon
            const nodeElement = node.filter(n => n.id === classNode.id);
            nodeElement.select(".expand-icon").text(classNode.collapsed ? "+" : "-");
            nodeElement.attr("data-collapsed", classNode.collapsed);
            
            // Get all method nodes for this class
            const methodNodes = classNode.methods;
            
            // Update visibility of class methods and their connections
            if (classNode.collapsed) {
                // Hide all method nodes
                node.filter(n => n.parent_class === classNode.name)
                    .style("display", "none");
                
                // Hide links to/from these methods
                link.filter(l => {
                    const sourceNode = graphData.nodes[l.source.id];
                    const targetNode = graphData.nodes[l.target.id];
                    return sourceNode.parent_class === classNode.name || 
                           targetNode.parent_class === classNode.name;
                }).style("display", "none");
            } else {
                // Show all method nodes
                node.filter(n => n.parent_class === classNode.name)
                    .style("display", "");
                
                // Show links to/from these methods
                link.filter(l => {
                    const sourceNode = graphData.nodes[l.source.id];
                    const targetNode = graphData.nodes[l.target.id];
                    return sourceNode.parent_class === classNode.name || 
                           targetNode.parent_class === classNode.name;
                }).style("display", "");
                
                // Re-run simulation to update layout
                simulation.alpha(0.3).restart();
            }
        }
        
        // Initialize visibility based on collapsed state
        function initializeVisibility() {
            // Hide all nodes and links for collapsed classes
            graphData.nodes.forEach(n => {
                if (n.type === "class_container" && n.collapsed) {
                    // Hide all method nodes for this class
                    node.filter(d => d.parent_class === n.name)
                        .style("display", "none");
                    
                    // Hide links to/from these methods
                    link.filter(l => {
                        const sourceNode = graphData.nodes[l.source.id];
                        const targetNode = graphData.nodes[l.target.id];
                        return sourceNode.parent_class === n.name || 
                               targetNode.parent_class === n.name;
                    }).style("display", "none");
                }
            });
        }
        
        // Show function details for regular nodes
        function showFunctionDetails(event, d) {
            const detailsDiv = document.getElementById("functionDetails");
            const fnTitle = document.getElementById("selectedFunction");
            const fileInfo = document.getElementById("fileInfo");
            const paramsTable = document.getElementById("paramsTable").getElementsByTagName("tbody")[0];
            
            // Clear previous data
            paramsTable.innerHTML = "";
            
            // Update details
            if (d.type === "class_container") {
                fnTitle.textContent = `Class: ${d.name}`;
                fileInfo.textContent = `File: ${d.filepath}`;
                
                const row = paramsTable.insertRow();
                const cell = row.insertCell(0);
                cell.colSpan = 3;
                cell.textContent = `Contains ${d.methods.length} methods`;
            } else {
                // Format function name with class if applicable
                const displayName = d.parent_class ? `${d.parent_class}.${d.name}` : d.name;
                fnTitle.textContent = displayName + "()";
                fileInfo.textContent = "File: " + d.filepath + ":" + d.line;
                
                // Add parameters
                if (d.params.length > 0) {
                    d.params.forEach(param => {
                        const row = paramsTable.insertRow();
                        const nameCell = row.insertCell(0);
                        const valueCell = row.insertCell(1);
                        const typeCell = row.insertCell(2);
                        
                        nameCell.textContent = param.name;
                        valueCell.textContent = param.value;
                        typeCell.textContent = param.type;
                    });
                } else {
                    const row = paramsTable.insertRow();
                    const cell = row.insertCell(0);
                    cell.colSpan = 3;
                    cell.textContent = "No parameters";
                }
            }
            
            // Show details div
            detailsDiv.style.display = "block";
            
            // Highlight connected nodes and links
            highlightConnections(d);
        }
        
        function highlightConnections(selectedNode) {
            // Reset previous highlight
            node.selectAll("circle").attr("r", 10);
            node.selectAll("rect")
                .attr("width", 20)
                .attr("height", 20)
                .attr("x", -10)
                .attr("y", -10);
            
            // Find connected nodes
            const linkedNodeIds = new Set();
            
            // For class containers, consider all methods as "connected"
            if (selectedNode.type === "class_container") {
                selectedNode.methods.forEach(methodId => {
                    linkedNodeIds.add(methodId);
                });
                
                // Also find connections to/from class methods
                graphData.links.forEach(link => {
                    const sourceNode = graphData.nodes[link.source.id];
                    const targetNode = graphData.nodes[link.target.id];
                    
                    if (sourceNode.parent_class === selectedNode.name && !linkedNodeIds.has(link.target.id)) {
                        linkedNodeIds.add(link.target.id);
                    }
                    
                    if (targetNode.parent_class === selectedNode.name && !linkedNodeIds.has(link.source.id)) {
                        linkedNodeIds.add(link.source.id);
                    }
                });
            } else {
                // Regular node connections
                
                // If this is a class method, also highlight the class container
                if (selectedNode.parent_class) {
                    // Find class container node
                    const classNode = graphData.nodes.find(n => 
                        n.type === "class_container" && n.name === selectedNode.parent_class);
                    
                    if (classNode) {
                        linkedNodeIds.add(classNode.id);
                    }
                }
                
                // Find outgoing connections
                graphData.links.forEach(link => {
                    if (link.source.id === selectedNode.id) {
                        linkedNodeIds.add(link.target.id);
                    }
                });
                
                // Find incoming connections
                graphData.links.forEach(link => {
                    if (link.target.id === selectedNode.id) {
                        linkedNodeIds.add(link.source.id);
                    }
                });
            }
            
            // Highlight selected node
            if (selectedNode.type === "class_container") {
                // Enlarge rectangle for selected class
                node.filter(d => d.id === selectedNode.id)
                    .select("rect")
                    .attr("width", 26)
                    .attr("height", 26)
                    .attr("x", -13)
                    .attr("y", -13)
                    .attr("stroke-width", 3);
            } else {
                // Enlarge circle for selected function/method
                node.filter(d => d.id === selectedNode.id)
                    .select("circle")
                    .attr("r", 15)
                    .attr("stroke-width", 3);
            }
            
            // Highlight connected nodes
            node.filter(d => linkedNodeIds.has(d.id)).each(function(d) {
                const element = d3.select(this);
                
                if (d.type === "class_container") {
                    element.select("rect")
                        .attr("width", 24)
                        .attr("height", 24)
                        .attr("x", -12)
                        .attr("y", -12)
                        .attr("stroke-width", 2.5);
                } else {
                    element.select("circle")
                        .attr("r", 12)
                        .attr("stroke-width", 2.5);
                }
            });
            
            // Highlight relevant links
            link.attr("stroke-width", d => 
                (d.source.id === selectedNode.id || d.target.id === selectedNode.id) 
                    ? 3 : 1.5
            );
            
            // Adjust opacity for nodes
            node.style("opacity", d => {
                // Keep class containers and their methods visible if expanded
                if (selectedNode.type === "class_container" && !selectedNode.collapsed) {
                    if (d.id === selectedNode.id || linkedNodeIds.has(d.id) || d.parent_class === selectedNode.name) {
                        return 1;
                    }
                }
                
                return (d.id === selectedNode.id || linkedNodeIds.has(d.id)) ? 1 : 0.3;
            });
            
            // Adjust opacity for links
            link.style("opacity", d => {
                // For class containers, keep links to/from methods visible
                if (selectedNode.type === "class_container") {
                    const sourceNode = graphData.nodes[d.source.id];
                    const targetNode = graphData.nodes[d.target.id];
                    
                    if (sourceNode.parent_class === selectedNode.name || 
                        targetNode.parent_class === selectedNode.name) {
                        return 1;
                    }
                }
                
                return (d.source.id === selectedNode.id || d.target.id === selectedNode.id) ? 1 : 0.1;
            });
        }
        
        // Reset view button
        document.getElementById("resetBtn").addEventListener("click", () => {
            svg.transition().duration(750).call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
            
            // Reset node highlighting
            node.style("opacity", 1);
            link.style("opacity", 0.6);
            
            node.filter(d => d.type === "class_container").each(function(d) {
                const element = d3.select(this);
                element.select("rect")
                    .attr("width", 20)
                    .attr("height", 20)
                    .attr("x", -10)
                    .attr("y", -10)
                    .attr("stroke-width", 2);
            });
            
            node.filter(d => d.type !== "class_container").each(function(d) {
                const element = d3.select(this);
                element.select("circle")
                    .attr("r", 10)
                    .attr("stroke-width", 2);
            });
            
            link.attr("stroke-width", 1.5);
            
            // Show all nodes
            expandAllClasses();
            
            // Hide function details
            document.getElementById("functionDetails").style.display = "none";
        });
        
        // Expand/collapse all classes functions
        function expandAllClasses() {
            graphData.nodes.forEach(node => {
                if (node.type === "class_container" && node.collapsed) {
                    toggleClassNode(node);
                }
            });
        }
        
        function collapseAllClasses() {
            graphData.nodes.forEach(node => {
                if (node.type === "class_container" && !node.collapsed) {
                    toggleClassNode(node);
                }
            });
        }
        
        // Search functionality
        document.getElementById("searchInput").addEventListener("input", function() {
            const searchTerm = this.value.toLowerCase();
            
            // Reset function details if search changes
            document.getElementById("functionDetails").style.display = "none";
            
            if (searchTerm === "") {
                // If search is cleared, reset all visibility
                node.style("opacity", 1);
                link.style("opacity", 0.6);
                
                // Restore collapsed/expanded state
                initializeVisibility();
                return;
            }
            
            // Find matching nodes
            const matchingNodes = new Set();
            
            graphData.nodes.forEach(n => {
                const name = n.name.toLowerCase();
                const filename = n.filename.toLowerCase();
                
                if (name.includes(searchTerm) || filename.includes(searchTerm)) {
                    matchingNodes.add(n.id);
                    
                    // For class methods, include their class container
                    if (n.parent_class) {
                        const classNode = graphData.nodes.find(c => 
                            c.type === "class_container" && c.name === n.parent_class);
                        if (classNode) {
                            matchingNodes.add(classNode.id);
                        }
                    }
                    
                    // For class containers, include all their methods
                    if (n.type === "class_container") {
                        n.methods.forEach(methodId => {
                            matchingNodes.add(methodId);
                        });
                    }
                }
            });
            
            // Show matching nodes, dim others
            node.style("opacity", d => matchingNodes.has(d.id) ? 1 : 0.2);
            
            // Show links between matching nodes, dim others
            link.style("opacity", d => 
                (matchingNodes.has(d.source.id) && matchingNodes.has(d.target.id)) ? 0.8 : 0.1
            );
            
            // Make sure all matching nodes from classes are visible
            graphData.nodes.forEach(n => {
                if (n.type === "class_container" && matchingNodes.has(n.id) && n.collapsed) {
                    // Auto-expand class if it matches search
                    toggleClassNode(n);
                }
            });
        });
        
        // Add event listeners for expand/collapse all
        document.getElementById("expandAllBtn").addEventListener("click", expandAllClasses);
        document.getElementById("collapseAllBtn").addEventListener("click", collapseAllClasses);
    </script>
</body>
</html>
''')
        
        print(f"Interactive HTML visualization generated: {output_path}")
        return output_path


# Example decorators and helper functions for easy use
def trace_and_visualize(func):
    """Decorator to trace and visualize a function call."""
    def wrapper(*args, **kwargs):
        tracer = FunctionCallTracer()
        tracer.start_tracing()
        try:
            result = func(*args, **kwargs)
        finally:
            tracer.stop_tracing()
            tracer.generate_mermaid_diagram()
            tracer.generate_html_visualization()
        return result
    return wrapper

def run_with_tracing(func, *args, **kwargs):
    """Run a function with tracing and generate visualizations."""
    tracer = FunctionCallTracer()
    tracer.start_tracing()
    try:
        result = func(*args, **kwargs)
    finally:
        tracer.stop_tracing()
        tracer.generate_mermaid_diagram()
        tracer.generate_html_visualization()
    return result

from functools import wraps
from unittest.mock import patch

def test_traced_patch(*patch_args, **patch_kwargs):
    """Combine @patch and @trace_and_visualize decorators for test methods."""
    def decorator(func):
        # Apply the patch decorator first
        patched_func = patch(*patch_args, **patch_kwargs)(func)
        
        # Then apply the tracing decorator
        @wraps(patched_func)
        def wrapper(*args, **kwargs):
            tracer = FunctionCallTracer()
            tracer.start_tracing()
            try:
                result = patched_func(*args, **kwargs)
            finally:
                tracer.stop_tracing()
                tracer.generate_html_visualization(f"{func.__name__}_trace.html")
            return result
        return wrapper
    return decorator