import sys
import os
from typing import Set
import json
import functools

class FunctionCallTracerWithReturn:
    def __init__(self, output_dir: str = '.', include_stdlib: list = [], max_depth: int = None):
        self.output_dir = output_dir
        self.include_stdlib = include_stdlib # pass library path as list of string
        self.max_depth = max_depth  # Maximum call depth to trace
        self.call_graph = {}  # Store function calls and their relationships
        self.func_params = {}  # Store function parameters
        self.current_stack = []  # Track current call stack
        self.excluded_paths = set()  # Paths to exclude
        self.entry_point = None  # Track the first function called
        
        # Add sequence tracking
        self.sequence_counter = 0
        self.call_sequence = {}  # Maps function ID to its call sequence number
        
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
        
        # Add sequence number to parameters
        self.sequence_counter += 1
        params['__sequence__'] = (str(self.sequence_counter), 'int')
        self.call_sequence[func_id] = self.sequence_counter
        
        self.func_params[func_id] = params
        
        # Associate function ID with call frame for return value tracking
        self.frame_to_func_id = getattr(self, 'frame_to_func_id', {})
        self.frame_to_func_id[id(frame)] = func_id
        
        # Update stack
        self.current_stack.append(func_id)
        
        # Return function to handle return and exception events
        return self.trace_events

    def trace_events(self, frame, event, arg):
        """
        Trace function returns and exceptions.
        
        Args:
            frame: The current stack frame
            event: The event type ('call', 'line', 'return', 'exception')
            arg: For 'return' - the return value; for 'exception' - a tuple (exception, value, traceback)
        """
        frame_id = id(frame)
        
        if event == 'return' and hasattr(self, 'frame_to_func_id') and frame_id in self.frame_to_func_id:
            func_id = self.frame_to_func_id[frame_id]
            
            # Store the return value
            return_value = arg  # 'arg' contains the return value in 'return' events
            
            try:
                # Get a representation of the return value
                return_repr = repr(return_value)
                return_type = type(return_value).__name__
                
                # Truncate very long representations
                if len(return_repr) > 1000:
                    return_repr = return_repr[:997] + "..."
                
                # Store with the function's parameters
                if func_id in self.func_params:
                    self.func_params[func_id]['__return_value__'] = (return_repr, return_type)
                
                # Clean up the frame tracking to avoid memory leaks
                del self.frame_to_func_id[frame_id]
            except Exception as e:
                # If we can't represent the return value, at least note that there was one
                if func_id in self.func_params:
                    self.func_params[func_id]['__return_value__'] = (f"<unprintable: {str(e)}>", "unknown")
            
            # Update stack on return
            if self.current_stack:
                self.current_stack.pop()
        
        elif event == 'exception' and hasattr(self, 'frame_to_func_id') and frame_id in self.frame_to_func_id:
            # For exceptions, arg is (exception, value, traceback)
            exc_type, exc_value, exc_traceback = arg
            func_id = self.frame_to_func_id[frame_id]
            
            # Create a representation of the exception
            try:
                exc_name = exc_type.__name__
                exc_msg = str(exc_value)
                
                # Truncate very long exception messages
                if len(exc_msg) > 500:
                    exc_msg = exc_msg[:497] + "..."
                
                # Store with the function's parameters
                if func_id in self.func_params:
                    self.func_params[func_id]['__exception__'] = (f"{exc_name}: {exc_msg}", "exception")
                    
                    # Set a flag to indicate this function raised an exception
                    self.func_params[func_id]['__has_exception__'] = ('True', 'bool')
                    
                    # Optionally capture traceback details
                    tb_entries = []
                    tb = exc_traceback
                    while tb:
                        frame = tb.tb_frame
                        filename = frame.f_code.co_filename
                        name = frame.f_code.co_name
                        lineno = tb.tb_lineno
                        tb_entries.append(f"{os.path.basename(filename)}:{name}:{lineno}")
                        tb = tb.tb_next
                    
                    if tb_entries:
                        tb_str = " -> ".join(tb_entries)
                        if len(tb_str) > 500:
                            tb_str = tb_str[:497] + "..."
                        self.func_params[func_id]['__traceback__'] = (tb_str, "traceback")
                
                # Don't clean up the frame tracking yet since the function hasn't returned
            except Exception as e:
                # If we can't represent the exception, at least note that there was one
                if func_id in self.func_params:
                    self.func_params[func_id]['__exception__'] = (f"<unprintable exception: {str(e)}>", "exception")
                    self.func_params[func_id]['__has_exception__'] = ('True', 'bool')
        
        # Continue tracing
        return self.trace_events
    
    def start_tracing(self):
        """Start tracing function calls."""
        sys.settrace(self.trace_calls)
    
    def stop_tracing(self):
        """Stop tracing function calls."""
        sys.settrace(None)
    
    def generate_html_visualization(self, filename: str = 'function_calls.html'):
        """Generate an interactive HTML visualization."""
        return FunctionVisualizerWithReturn.generate_html(self, filename)


class FunctionVisualizerWithReturn:
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
                "params": {},
                "methods": [],  # Will store indices of method nodes
                "collapsed": True,  # Initially collapsed
                "sequence": float('inf')  # Default to high number, will set to min of methods
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
            
            # Get all params including special ones
            params = {}
            if node_id in tracer.func_params:
                params = tracer.func_params[node_id]
            
            # Get sequence number
            sequence = float('inf')
            if node_id in tracer.call_sequence:
                sequence = tracer.call_sequence[node_id]
            elif "__sequence__" in params:
                sequence = int(params["__sequence__"][0])
                
            # If this is a class method, update the class's sequence to the earliest method call
            if parent_class and class_name in class_nodes:
                class_node_idx = class_nodes[parent_class]
                if sequence < nodes[class_node_idx]["sequence"]:
                    nodes[class_node_idx]["sequence"] = sequence
            
            # Create node
            node = {
                "id": node_index,
                "name": display_name,
                "filename": filename,
                "filepath": filepath,
                "line": line_no,
                "type": node_type,
                "params": params,
                "parent_class": parent_class,  # Reference to parent class if applicable
                "sequence": sequence  # Add sequence number to node
            }
            
            # Skip if this is a class method (we'll handle these differently)
            if parent_class:
                # Store which methods belong to which class
                class_node_idx = class_nodes[parent_class]
                nodes[class_node_idx]["methods"].append(node_index)
            
            nodes.append(node)
            node_map[node_id] = node_index
            node_index += 1
        
        # Create links between nodes
        for parent in tracer.call_graph:
            for child in tracer.call_graph[parent]:
                if parent in node_map and child in node_map:
                    parent_seq = tracer.call_sequence.get(parent, float('inf'))
                    child_seq = tracer.call_sequence.get(child, float('inf'))
                    links.append({
                        "source": node_map[parent],
                        "target": node_map[child],
                        "sourceSeq": parent_seq,
                        "targetSeq": child_seq
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
                min-height: 600px;
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
                z-index: 1000;
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
            .text-bg {
                fill: white;
                fill-opacity: 0.9;
            }
            .link {
                stroke: #999;
                stroke-opacity: 0.6;
                stroke-width: 1.5px;
                fill: none;
            }
            .sequence-label {
                font-size: 10px;
                fill: #666;
            }
            .controls {
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            .controls-left {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 10px;
            }
            .controls button {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                white-space: nowrap;
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
            #verticalSequentialBtn {
                background-color: #ff5722;
                color: white;
            }
            #verticalSequentialBtn:hover {
                background-color: #e64a19;
            }
            .legend {
                display: flex;
                justify-content: center;
                margin-top: 10px;
                font-size: 12px;
                flex-wrap: wrap;
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
            
            /* Exception styling */
            .exception-title {
                color: #d9534f;
                margin-top: 15px;
                margin-bottom: 5px;
            }
            .exception-text {
                color: #d9534f;
                font-family: monospace;
            }
            .traceback-info {
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
                background-color: #f8f8f8;
                padding: 5px;
                border-radius: 4px;
                border-left: 3px solid #d9534f;
                margin-top: 5px;
            }
            
            /* Return value styling */
            .return-value {
                font-family: monospace;
                background-color: #f8f8f8;
                padding: 5px;
                border-radius: 4px;
                border-left: 3px solid #4285f4;
                margin-top: 5px;
            }
            
            /* Sequence number badge */
            .sequence-badge {
                display: inline-block;
                background: #666;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                text-align: center;
                line-height: 20px;
                margin-right: 5px;
                font-size: 11px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Function Call Visualization</h1>
            
            <div class="controls">
                <div class="controls-left">
                    <button id="resetBtn">Reset View</button>
                    <button id="expandAllBtn">Expand All Classes</button>
                    <button id="collapseAllBtn">Collapse All Classes</button>
                    <button id="verticalSequentialBtn">Vertical Layout</button>
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
                <p id="sequenceInfo">Sequence: </p>
                <div id="returnValueInfo"></div>
                <div id="exceptionInfo"></div>
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
            
            // Create links with curved paths
            const link = g.append("g")
                .selectAll("path")
                .data(graphData.links)
                .enter()
                .append("path")
                .attr("class", "link");
            
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
                        .attr("fill", d => {
                            // Use red for nodes with exceptions
                            if (d.params.__has_exception__) {
                                return "#d9534f";  // Red for exceptions
                            }
                            return colorMap[d.type];
                        })
                        .attr("stroke", d => {
                            if (d.params.__has_exception__) {
                                return "#a94442";  // Darker red for exception stroke
                            }
                            return d3.rgb(colorMap[d.type]).darker(0.5);
                        })
                        .attr("stroke-width", 2);
                    
                    // Add sequence number inside the circle for better visibility
                    if (d.sequence !== Infinity) {
                        nodeElement.append("text")
                            .attr("class", "sequence-number")
                            .attr("text-anchor", "middle")
                            .attr("dominant-baseline", "central")
                            .attr("font-size", 8)
                            .attr("font-weight", "bold")
                            .attr("fill", "white")
                            .text(d.sequence);
                    }
                }
            });
            
            // Add labels to nodes with sequence numbers
            node.append("text")
                .attr("dx", 15)
                .attr("dy", 5)
                .text(d => {
                    let displayText = "";
                    if (d.type === "class_container") {
                        displayText = `Class ${d.name}`;
                    } else if (d.parent_class) {
                        displayText = `${d.parent_class}.${d.name}()`;
                    } else {
                        displayText = d.name + "()";
                    }
                    
                    // Add sequence number prefix if available and not infinity
                    if (d.sequence !== Infinity) {
                        displayText = `[${d.sequence}] ${displayText}`;
                    }
                    
                    return displayText;
                });
                
            // Add sequence numbers to links
            const linkLabels = g.append("g")
                .selectAll(".link-label")
                .data(graphData.links)
                .enter()
                .append("text")
                .attr("class", "sequence-label")
                .attr("text-anchor", "middle")
                .attr("dy", -5)
                .text(d => {
                    return `${d.sourceSeq}→${d.targetSeq}`;
                });
                
            // Tooltip
            const tooltip = d3.select("#tooltip");
            
            // Set up the simulation
            const simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collide", d3.forceCollide().radius(50));
                
            // Flags to track layout modes
            let isVerticalLayout = false;
            let isSequentialLayout = false;
            let isSequentialVertical = false;
            
            // Initialize the visualization with the force layout
            initForceLayout();
                
            // Initialize visibility based on collapsed classes
            initializeVisibility();
            
            node.on("mouseover", function(event, d) {
                // Show tooltip
                tooltip.transition().duration(200).style("opacity", .9);
                
                // Create tooltip content
                let tooltipContent = "";
                
                if (d.type === "class_container") {
                    tooltipContent = `<strong>Class ${d.name}</strong><br/>`;
                    tooltipContent += `Contains ${d.methods.length} methods<br/>`;
                    if (d.sequence !== Infinity) {
                        tooltipContent += `First called at sequence: <strong>${d.sequence}</strong><br/>`;
                    }
                } else if (d.parent_class) {
                    tooltipContent = `<strong>${d.parent_class}.${d.name}()</strong><br/>`;
                    if (d.sequence !== Infinity) {
                        tooltipContent += `Sequence: <strong>${d.sequence}</strong><br/>`;
                    }
                } else {
                    tooltipContent = `<strong>${d.name}()</strong><br/>`;
                    if (d.sequence !== Infinity) {
                        tooltipContent += `Sequence: <strong>${d.sequence}</strong><br/>`;
                    }
                }
                
                tooltipContent += `File: ${d.filename}:${d.line}<br/>`;
                
                // Add return value if available
                if (d.params.__return_value__) {
                    tooltipContent += `<strong>Returns:</strong> `;
                    tooltipContent += `<span class="param-value">${d.params.__return_value__[0]}</span> `;
                    tooltipContent += `<span class="param-type">(${d.params.__return_value__[1]})</span><br/>`;
                }
                
                // Add exception info if available
                if (d.params.__exception__) {
                    tooltipContent += `<strong style="color:#d9534f">Exception:</strong> `;
                    tooltipContent += `<span class="exception-text">${d.params.__exception__[0]}</span><br/>`;
                }
                
                // Add parameters
                const standardParams = Object.entries(d.params).filter(
                    ([key]) => !key.startsWith('__')
                );
                
                if (standardParams.length > 0) {
                    tooltipContent += `<strong>Parameters:</strong><br/>`;
                    standardParams.forEach(([key, [value, type]]) => {
                        tooltipContent += `<span class="param-name">${key}</span>: `;
                        tooltipContent += `<span class="param-value">${value}</span> `;
                        tooltipContent += `<span class="param-type">(${type})</span><br/>`;
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
                link.attr("d", d => {
                    const source = d.source;
                    const target = d.target;
                    return `M${source.x},${source.y}
                            C${source.x},${(source.y + target.y) / 2}
                            ${target.x},${(source.y + target.y) / 2}
                            ${target.x},${target.y}`;
                });
                
                // Update link label positions
                linkLabels.attr("x", d => (d.source.x + d.target.x) / 2)
                    .attr("y", d => (d.source.y + d.target.y) / 2);
                
                node.attr("transform", d => `translate(${d.x},${d.y})`);
            });
            
            // Drag functions
            function dragstarted(event, d) {
                if (!isVerticalLayout && !isSequentialLayout && !isSequentialVertical && !event.active) 
                    simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                if (!isVerticalLayout && !isSequentialLayout && !isSequentialVertical) {
                    // Only allow free dragging in force layout mode
                    d.fx = event.x;
                    d.fy = event.y;
                } else if (isSequentialLayout) {
                    // In sequential layout, only allow vertical movement
                    d.fx = d.x;
                    d.fy = event.y;
                } else if (isSequentialVertical) {
                    // In vertical sequential layout, only allow horizontal movement
                    d.fx = event.x;
                    d.fy = d.y;
                } else {
                    // In vertical layout, only allow horizontal movement
                    d.fx = event.x;
                    d.fy = d.y;
                }
            }
            
            function dragended(event, d) {
                if (!isVerticalLayout && !isSequentialLayout && !isSequentialVertical && !event.active) 
                    simulation.alphaTarget(0);
                
                // In fixed layouts, keep fixed positions
                if (!isVerticalLayout && !isSequentialLayout && !isSequentialVertical) {
                    d.fx = null;
                    d.fy = null;
                }
            }
            
            // Initialize with force layout
            function initForceLayout() {
                // Add marker end for links
                link.attr("marker-end", "url(#arrowhead)");
                
                // Clear any fixed positions
                graphData.nodes.forEach(d => {
                    d.fx = null;
                    d.fy = null;
                });
                
                // Run simulation
                simulation.alpha(1).restart();
                
                isVerticalLayout = false;
                isSequentialLayout = false;
                isSequentialVertical = false;
                
                // Hide link sequence labels in force layout
                linkLabels.style("display", "none");
            }
                 
            // Function to apply a vertical sequential layout based on execution order
            function applyVerticalSequentialLayout() {
                // Sort nodes by sequence number
                const sortedNodes = [...graphData.nodes].sort((a, b) => {
                    // Handle infinity values - put them at the end
                    if (a.sequence === Infinity && b.sequence === Infinity) return 0;
                    if (a.sequence === Infinity) return 1;
                    if (b.sequence === Infinity) return -1;
                    return a.sequence - b.sequence;
                });
                
                // Position nodes in a strict vertical layout
                const nodeHeight = 80;  // Vertical space between nodes
                const topMargin = 50;
                const leftPosition = width / 2;
                
                // Position nodes in a vertical line based on sequence
                sortedNodes.forEach((node, index) => {
                    // Position nodes in the center column
                    node.x = leftPosition;
                    node.y = topMargin + (index * nodeHeight);
                    
                    // Fix node positions
                    node.fx = node.x;
                    node.fy = node.y;
                });
                
                // Update node positions
                node.attr("transform", d => `translate(${d.x},${d.y})`);
                
                // Update links with simple curved paths
                link.attr("d", d => {
                    const source = graphData.nodes[d.source.id];
                    const target = graphData.nodes[d.target.id];
                    
                    // Create curved paths - more pronounced curves for links spanning multiple nodes
                    const sourceIndex = sortedNodes.findIndex(n => n.id === source.id);
                    const targetIndex = sortedNodes.findIndex(n => n.id === target.id);
                    const distance = Math.abs(targetIndex - sourceIndex);
                    
                    // Calculate curve intensity based on distance
                    const curveOffset = Math.min(100, distance * 15);
                    
                    if (sourceIndex < targetIndex) {
                        // Downward link
                        return `M${source.x},${source.y}
                                C${source.x + curveOffset},${(source.y + target.y) / 2}
                                ${target.x + curveOffset},${(source.y + target.y) / 2}
                                ${target.x},${target.y}`;
                    } else {
                        // Upward link (less common in sequences)
                        return `M${source.x},${source.y}
                                C${source.x - curveOffset},${(source.y + target.y) / 2}
                                ${target.x - curveOffset},${(source.y + target.y) / 2}
                                ${target.x},${target.y}`;
                    }
                });
                
                // Update link label positions
                linkLabels.attr("x", d => {
                    const source = graphData.nodes[d.source.id];
                    const target = graphData.nodes[d.target.id];
                    
                    // Position label to the side of the curve
                    const sourceIndex = sortedNodes.findIndex(n => n.id === source.id);
                    const targetIndex = sortedNodes.findIndex(n => n.id === target.id);
                    const distance = Math.abs(targetIndex - sourceIndex);
                    const curveOffset = Math.min(100, distance * 15);
                    
                    return sourceIndex < targetIndex ? 
                        (source.x + target.x) / 2 + curveOffset/2 : 
                        (source.x + target.x) / 2 - curveOffset/2;
                })
                .attr("y", d => (d.source.y + d.target.y) / 2)
                .style("display", "");
                
                // Stop the simulation
                simulation.stop();
                
                // Add white background to text for better readability
                node.selectAll("text").each(function() {
                    const text = d3.select(this);
                    
                    // Remove any existing backgrounds
                    text.selectAll("rect.text-bg").remove();
                    
                    // Get text dimensions
                    const bbox = text.node().getBBox();
                    
                    // Insert a white background rectangle behind the text
                    text.insert("rect", "text")
                        .attr("class", "text-bg")
                        .attr("x", bbox.x - 2)
                        .attr("y", bbox.y - 2)
                        .attr("width", bbox.width + 4)
                        .attr("height", bbox.height + 4);
                });
                
                isVerticalLayout = false;
                isSequentialLayout = false;
                isSequentialVertical = true;
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
                
                // Hide link labels
                linkLabels.filter(l => {
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
                
                // Show link labels if in a layout that uses them
                if (isVerticalLayout || isSequentialLayout || isSequentialVertical) {
                    linkLabels.filter(l => {
                        const sourceNode = graphData.nodes[l.source.id];
                        const targetNode = graphData.nodes[l.target.id];
                        return sourceNode.parent_class === classNode.name || 
                               targetNode.parent_class === classNode.name;
                    }).style("display", "");
                }
                
                // Update the layout accordingly
                if (isSequentialVertical) {
                    applyVerticalSequentialLayout();
                } else {
                    // Re-run simulation to update layout
                    simulation.alpha(0.3).restart();
                }
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
                    
                    // Hide link labels
                    linkLabels.filter(l => {
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
            const sequenceInfo = document.getElementById("sequenceInfo");
            const returnValueInfo = document.getElementById("returnValueInfo");
            const exceptionInfo = document.getElementById("exceptionInfo");
            const paramsTable = document.getElementById("paramsTable").getElementsByTagName("tbody")[0];
            
            // Clear previous data
            paramsTable.innerHTML = "";
            returnValueInfo.innerHTML = "";
            exceptionInfo.innerHTML = "";
            
            // Update details
            if (d.type === "class_container") {
                fnTitle.textContent = `Class: ${d.name}`;
                fileInfo.textContent = `File: ${d.filepath}`;
                sequenceInfo.textContent = d.sequence !== Infinity ? 
                    `First called at sequence: ${d.sequence}` : 'Sequence: Not called directly';
                
                const row = paramsTable.insertRow();
                const cell = row.insertCell(0);
                cell.colSpan = 3;
                cell.textContent = `Contains ${d.methods.length} methods`;
            } else {
                // Format function name with class if applicable
                const displayName = d.parent_class ? `${d.parent_class}.${d.name}` : d.name;
                fnTitle.textContent = displayName + "()";
                fileInfo.textContent = "File: " + d.filepath + ":" + d.line;
                sequenceInfo.textContent = d.sequence !== Infinity ? 
                    `Sequence number: ${d.sequence}` : 'Sequence: Not called directly';
                
                // Add return value if available
                if (d.params.__return_value__) {
                    returnValueInfo.innerHTML = `
                        <h4>Return Value:</h4>
                        <div class="return-value">
                            <span class="param-value">${d.params.__return_value__[0]}</span>
                            <span class="param-type">(${d.params.__return_value__[1]})</span>
                        </div>
                    `;
                }
                
                // Add exception info if available
                if (d.params.__exception__) {
                    let exceptionHtml = `
                        <h4 class="exception-title">Exception:</h4>
                        <div class="exception-value">
                            <span class="exception-text">${d.params.__exception__[0]}</span>
                        </div>
                    `;
                    
                    // Add traceback if available
                    if (d.params.__traceback__) {
                        exceptionHtml += `
                            <h5>Traceback:</h5>
                            <div class="traceback-info">
                                ${d.params.__traceback__[0]}
                            </div>
                        `;
                    }
                    
                    exceptionInfo.innerHTML = exceptionHtml;
                }
                
                // Add parameters (excluding special params starting with __)
                const standardParams = Object.entries(d.params).filter(
                    ([key]) => !key.startsWith('__')
                );
                
                if (standardParams.length > 0) {
                    standardParams.forEach(([key, [value, type]]) => {
                        const row = paramsTable.insertRow();
                        const nameCell = row.insertCell(0);
                        const valueCell = row.insertCell(1);
                        const typeCell = row.insertCell(2);
                        
                        nameCell.textContent = key;
                        valueCell.textContent = value;
                        typeCell.textContent = type;
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
            
            // Highlight execution sequence
            if (d.sequence !== Infinity) {
                highlightSequence(d);
            }
        }
        
        // Highlight nodes connected in the call graph
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
            
            // Reset link labels opacity
            linkLabels.style("opacity", 0.6);
        }
        
        // Function to highlight execution sequence
        function highlightSequence(selectedNode) {
            // Get the sequence number of the selected node
            const selectedSeq = selectedNode.sequence;
            if (selectedSeq === Infinity) return;
            
            // Find nodes that were called before and after the selected node
            const prevNodes = graphData.nodes.filter(n => 
                n.sequence !== Infinity && n.sequence < selectedSeq);
            
            const nextNodes = graphData.nodes.filter(n => 
                n.sequence !== Infinity && n.sequence > selectedSeq);
            
            // Create sequence groups
            const prevNodeIds = new Set(prevNodes.map(n => n.id));
            const nextNodeIds = new Set(nextNodes.map(n => n.id));
            
            // Adjust node styling to show sequence
            node.style("opacity", d => {
                if (d.id === selectedNode.id) return 1; // Selected node full opacity
                if (d.sequence === Infinity) return 0.2; // Non-sequenced nodes very dim
                if (prevNodeIds.has(d.id)) return 0.7; // Previous nodes medium opacity
                if (nextNodeIds.has(d.id)) return 0.5; // Next nodes lower opacity
                return 0.2; // Other nodes very dim
            });
            
            // Generate sequential path highlighting
            const sequentialPath = [];
            
            // Sort by sequence
            const executionSequence = graphData.nodes
                .filter(n => n.sequence !== Infinity)
                .sort((a, b) => a.sequence - b.sequence);
            
            // Highlight link labels for sequential calls
            linkLabels.style("opacity", d => {
                // Show sequence numbers for direct call sequence links
                return (d.sourceSeq !== Infinity && d.targetSeq !== Infinity) ? 0.9 : 0.1;
            });
        }
        
        // Reset view button
        document.getElementById("resetBtn").addEventListener("click", () => {
            // Reset zoom
            svg.transition().duration(750).call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
            
            // Reset node highlighting
            node.style("opacity", 1);
            link.style("opacity", 0.6);
            linkLabels.style("opacity", 0.6);
            
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
            
            // Clear fixed positions
            graphData.nodes.forEach(d => {
                d.fx = null;
                d.fy = null;
            });
            
            // Expand all classes
            expandAllClasses();
            
            // Hide function details
            document.getElementById("functionDetails").style.display = "none";
            
            // Reset to force layout
            initForceLayout();
        });
        
        // Layout buttons
        document.getElementById("verticalSequentialBtn").addEventListener("click", applyVerticalSequentialLayout);
        
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
        
        // Add event listeners for expand/collapse all
        document.getElementById("expandAllBtn").addEventListener("click", expandAllClasses);
        document.getElementById("collapseAllBtn").addEventListener("click", collapseAllClasses);
        
        // Search functionality
        document.getElementById("searchInput").addEventListener("input", function() {
            const searchTerm = this.value.toLowerCase();
            
            // Reset function details if search changes
            document.getElementById("functionDetails").style.display = "none";
            
            if (searchTerm === "") {
                // If search is cleared, reset all visibility
                node.style("opacity", 1);
                link.style("opacity", 0.6);
                linkLabels.style("opacity", isVerticalLayout || isSequentialLayout || isSequentialVertical ? 0.6 : 0);
                
                // Restore collapsed/expanded state
                initializeVisibility();
                return;
            }
            
            // Find matching nodes
            const matchingNodes = new Set();
            
            graphData.nodes.forEach(n => {
                const name = n.name.toLowerCase();
                const filename = n.filename.toLowerCase();
                const sequence = n.sequence !== Infinity ? n.sequence.toString() : '';
                
                // Extended search to include sequence numbers
                if (name.includes(searchTerm) || 
                    filename.includes(searchTerm) || 
                    sequence.includes(searchTerm)) {
                    
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
            
            // Show link labels for matching nodes
            linkLabels.style("opacity", d => 
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
    </script>
</body>
</html>''')
        
        print(f"Interactive HTML visualization generated: {output_path}")
        return output_path

# Example decorators and helper functions for easy use
def trace_and_visualize(func=None, include_stdlib=None):
    """
    A decorator that can trace libraries with or without wrapping a function.
    
    Can be used as:
    @trace_and_visualize(include_stdlib=['pandas'])
    def my_function():
        pass
    
    Args:
        func: The function to decorate (optional)
        include_stdlib: List of library names to trace
    """
    if include_stdlib is None:
        include_stdlib = []
        
    def create_wrapper(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            tracer = FunctionCallTracerWithReturn(include_stdlib=include_stdlib)
            tracer.start_tracing()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                tracer.stop_tracing()
                tracer.generate_html_visualization()
        return wrapper
    
    # Called as @trace_and_visualize
    if func is not None:
        return create_wrapper(func)
    
    # Called as @trace_and_visualize(include_stdlib=['pandas'])
    return create_wrapper