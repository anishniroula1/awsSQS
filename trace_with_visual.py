# Import the tracing tool
from FunctionCallTracerWithReturns import FunctionCallTracerWithReturn, trace_and_visualize, run_with_tracing

# Define some example functions
def __inner_calculation(x, y):
    return x * y + x

def calculate_area(length, width):
    return __inner_calculation(length, width)

def process_data(data_list):
    result = []
    for item in data_list:
        processed = transform_item(item)
        result.append(processed)
    return result

def transform_item(item):
    return item * 2

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return process_data(self.data)
    
    def __hidden_method(self, factor=2):
        return [x * factor for x in self.data]

# Method 1: Use the decorator
@trace_and_visualize
def main_decorated():
    # This function will be traced and visualized automatically
    area = calculate_area(5, 10)
    print(f"Area result: {area}")
    
    numbers = [1, 2, 3, 4, 5]
    processor = DataProcessor(numbers)
    processed = processor.process()
    hidden = processor._DataProcessor__hidden_method(3)  # Access private method
    
    print(f"Processed data: {processed}")
    print(f"Hidden processed: {hidden}")

# Method 2: Manual tracing
def main_manual():
    area = calculate_area(5, 10)
    print(f"Area result: {area}")
    
    numbers = [1, 2, 3, 4, 5]
    processor = DataProcessor(numbers)
    processed = processor.process()
    hidden = processor._DataProcessor__hidden_method(3)
    
    print(f"Processed data: {processed}")
    print(f"Hidden processed: {hidden}")

if __name__ == "__main__":
    # Option 1: Use the decorator approach
    main_decorated()
    
    # Option 2: Manual approach - uncomment to use
    # tracer = FunctionCallTracer()
    # tracer.start_tracing()
    # try:
    #     main_manual()
    # finally:
    #     tracer.stop_tracing()
    #     tracer.generate_mermaid_diagram('manual_trace.md')
    #     tracer.generate_graphviz_dot('manual_trace.dot')
    
    # Option 3: Use the helper function
    # run_with_tracing(main_manual)