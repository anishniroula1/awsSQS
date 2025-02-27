# Function Call Diagram

```mermaid
flowchart TD
    func0_DataProcessor.process["trace_with_visual.py<br>DataProcessor.process()"]
    func1_process["trace_with_visual.py<br>process()"]
    func2_inner_calculation["trace_with_visual.py<br>__inner_calculation()<br>x: 5 (int)<br>y: 10 (int)"]
    func3_init["__init__()"]
    func4_DataProcessor.hidden_method["trace_with_visual.py<br>DataProcessor.__hidden_method()<br>factor: 3 (int)"]
    func5_transform_item["trace_with_visual.py<br>transform_item()<br>item: 5 (int)"]
    func6_stop_tracing["FunctionCallTracer.py<br>stop_tracing()"]
    func7_DataProcessor.init["trace_with_visual.py<br>DataProcessor.__init__()<br>data: [1, 2, 3, 4, 5] (list)"]
    func8_<listcomp>["trace_with_visual.py<br><listcomp>()<br>.0: <list_iterat... (list_iterator)<br>factor: 3 (int)"]
    func9_hidden_method["trace_with_visual.py<br>__hidden_method()"]
    func10_process_data["trace_with_visual.py<br>process_data()<br>data_list: [1, 2, 3, 4, 5] (list)"]
    func11_main_decorated["trace_with_visual.py<br>main_decorated()"]
    func12_calculate_area["trace_with_visual.py<br>calculate_area()<br>length: 5 (int)<br>width: 10 (int)"]
    func11_main_decorated --> func12_calculate_area
    func12_calculate_area --> func2_inner_calculation
    func2_inner_calculation --> func3_init
    func7_DataProcessor.init --> func1_process
    func0_DataProcessor.process --> func10_process_data
    func10_process_data --> func5_transform_item
    func5_transform_item --> func5_transform_item
    func5_transform_item --> func9_hidden_method
    func4_DataProcessor.hidden_method --> func8_<listcomp>
    func8_<listcomp> --> func6_stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_DataProcessor.process utilMethod
    class func1_process utilMethod
    class func2_inner_calculation privateMethod
    class func3_init initMethod
    class func4_DataProcessor.hidden_method privateMethod
    class func5_transform_item privateMethod
    class func6_stop_tracing privateMethod
    class func7_DataProcessor.init privateMethod
    class func8_<listcomp> utilMethod
    class func9_hidden_method privateMethod
    class func10_process_data privateMethod
    class func11_main_decorated mainMethod
    class func12_calculate_area privateMethod
```
