import sys

def global_trace(frame, event, arg):
    """
    Trace function that gets called for every function call in the program.
    
    Args:
        frame: The current stack frame
        event: The event type ('call', 'line', 'return', 'exception')
        arg: Depends on the event type
    """
    if event == 'call':
        # A function is being called
        func_name = frame.f_code.co_name
        file_name = frame.f_code.co_filename
        line_no = frame.f_lineno
        
        # Skip built-in functions and methods
        if file_name == '<string>' or func_name.startswith('__'):
            return
        
        # Get local variables (parameters)
        locals_dict = frame.f_locals
        params = [f"{name}={repr(val)} ({type(val).__name__})" for name, val in locals_dict.items()]
        
        print(f"Function call: {file_name}:{func_name} at line {line_no}")
        if params:
            print(f"Parameters: {', '.join(params)}")
        print("-" * 40)
        
    return global_trace  # Return the function to continue tracing

# Example functions to trace
def calculate_area(length, width):
    return length * width

def process_data(data_list):
    result = []
    for item in data_list:
        processed = transform_item(item)
        result.append(processed)
    return result

def transform_item(item):
    return item * 2

# Main execution
def main():
    # Enable tracing
    sys.settrace(global_trace)
    
    # Run code that we want to trace
    area = calculate_area(5, 10)
    print(f"Area result: {area}")
    
    numbers = [1, 2, 3, 4, 5]
    processed = process_data(numbers)
    print(f"Processed data: {processed}")
    
    # Disable tracing
    sys.settrace(None)

if __name__ == "__main__":
    main()