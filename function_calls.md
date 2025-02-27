# Function Call Diagram

```mermaid
flowchart TD
    func0_transform_item["system_trace.py<br>transform_item()<br>item: 5 (int)"]
    func1_iner_method["system_trace.py<br>__iner_method()<br>length: 5 (int)<br>width: 10 (int)"]
    func2_Process.init["system_trace.py<br>Process.__init__()<br>data_list: [1, 2, 3, 4, 5] (list)<br>__class_name__: Process (class)"]
    func3_Process.process_data["system_trace.py<br>Process.process_data()<br>__class_name__: Process (class)"]
    func4_FunctionCallTracer.stop_tracing["FunctionCallTracer.py<br>FunctionCallTracer.stop_tracing()<br>__class_name__: FunctionCall... (class)"]
    func5_random_method["system_trace.py<br>random_method()<br>int: 5 (int)"]
    func6__test_method["system_trace.py<br>_test_method()<br>int: 5 (int)"]
    func7_main["system_trace.py<br>main()"]
    func8_calculate_area["system_trace.py<br>calculate_area()<br>length: 5 (int)<br>width: 10 (int)"]
    func7_main --> func8_calculate_area
    func8_calculate_area --> func1_iner_method
    func1_iner_method --> func6__test_method
    func6__test_method --> func5_random_method
    func5_random_method --> func2_Process.init
    func2_Process.init --> func3_Process.process_data
    func3_Process.process_data --> func0_transform_item
    func0_transform_item --> func0_transform_item
    func0_transform_item --> func4_FunctionCallTracer.stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_transform_item privateMethod
    class func1_iner_method privateMethod
    class func2_Process.init privateMethod
    class func3_Process.process_data privateMethod
    class func4_FunctionCallTracer.stop_tracing privateMethod
    class func5_random_method privateMethod
    class func6__test_method utilMethod
    class func7_main mainMethod
    class func8_calculate_area privateMethod
```
