# Python Function Call Tracer

A powerful, interactive visualization tool for understanding Python code execution flow.

## Overview

Python Function Call Tracer is a specialized tool designed to help developers understand and visualize the execution flow of their Python code. It traces function calls, including class methods, and generates interactive visualizations showing how functions call each other. This makes it particularly useful for understanding complex codebases, debugging, and code documentation.

## Features

- **Interactive Visualization** - Dynamic, interactive diagrams of function calls
- **Class Hierarchy Support** - View class relationships with expandable/collapsible class nodes
- **Parameter Inspection** - See function parameters and their types
- **Testing Framework Integration** - Works with unittest, pytest, and mocked functions
- **Execution Flow Tracking** - Follow the exact path of execution through your code
- **Code Navigation** - Click on functions to see detailed information
- **Color-Coded Visualization** - Different colors for classes, methods, and function types

## Quick Start Guide

### Basic Usage

```python
from function_tracer import trace_and_visualize

@trace_and_visualize
def main():
    result = calculate_something(5, 10)
    process_result(result)
    return result

if __name__ == "__main__":
    main()
```

### Manual Tracing

```python
from function_tracer import FunctionCallTracer

def my_function():
    # Your code here
    pass

tracer = FunctionCallTracer()
tracer.start_tracing()
my_function()
tracer.stop_tracing()
tracer.generate_html_visualization()
```

### With Testing Frameworks

```python
from function_tracer import trace_and_visualize
from unittest.mock import patch

@trace_and_visualize
@patch('module.function_to_mock')
def test_something(mock_function):
    mock_function.return_value = 'mocked result'
    # Your test code...
```

## Visualization Features

### Interactive Interface

The generated HTML visualization offers:

- **Zoom & Pan**: Navigate large call graphs easily
- **Expand/Collapse**: Toggle class methods visibility
- **Search**: Find specific functions quickly
- **Tooltips**: See function details on hover
- **Function Details**: Click nodes for parameter information

### Color Scheme

- **Blue**: Main methods
- **Green**: Regular functions
- **Yellow**: Private methods
- **Red**: Constructors
- **Purple**: Class methods
- **Violet**: Class containers

## Implementation Details

### How It Works

The tracer uses Python's `sys.settrace()` function to monitor function calls during execution. It builds a graph of the call relationships and collects parameter information. This data is then transformed into an interactive visualization using D3.js.

### Class Method Detection

The tracer intelligently detects class methods by checking for 'self' parameters and determines the class name. This allows it to group methods under their parent classes in the visualization.

### Mock Object Handling

For testing, the tracer includes special handling for mock objects created by libraries like unittest.mock. It attempts to identify the original function being mocked and displays appropriate information.

## Troubleshooting

### Common Issues

**Issue**: Visualization is too large to view easily  
**Solution**: Use the search function, or try tracing a smaller part of your code

**Issue**: Not seeing class methods properly  
**Solution**: Ensure you're creating proper class instances; anonymous instances may not track correctly

**Issue**: Missing function calls with patched methods  
**Solution**: Make sure the tracer decorator is outside (applied after) the patch decorator