# Function Call Diagram

```mermaid
flowchart TD
    func0_<listcomp>["trace_with_visual.py<br><listcomp>()<br>.0: <list_iterat... (list_iterator)<br>factor: 3 (int)"]
    func1_stop_tracing["FunctionCallTracer.py<br>stop_tracing()"]
    func2_inner_calculation["trace_with_visual.py<br>__inner_calculation()<br>x: 5 (int)<br>y: 10 (int)"]
    func3_transform_item["trace_with_visual.py<br>transform_item()<br>item: 5 (int)"]
    func4_process["trace_with_visual.py<br>process()"]
    func5_DataProcessor.init["trace_with_visual.py<br>DataProcessor.__init__()<br>data: [1, 2, 3, 4, 5] (list)"]
    func6_init["__init__()"]
    func7_process_data["trace_with_visual.py<br>process_data()<br>data_list: [1, 2, 3, 4, 5] (list)"]
    func8_calculate_area["trace_with_visual.py<br>calculate_area()<br>length: 5 (int)<br>width: 10 (int)"]
    func9_DataProcessor.hidden_method["trace_with_visual.py<br>DataProcessor.__hidden_method()<br>factor: 3 (int)"]
    func10_DataProcessor.process["trace_with_visual.py<br>DataProcessor.process()"]
    func11_hidden_method["trace_with_visual.py<br>__hidden_method()"]
    func12_main_manual["trace_with_visual.py<br>main_manual()"]
    func12_main_manual --> func8_calculate_area
    func8_calculate_area --> func2_inner_calculation
    func2_inner_calculation --> func6_init
    func5_DataProcessor.init --> func4_process
    func10_DataProcessor.process --> func7_process_data
    func7_process_data --> func3_transform_item
    func3_transform_item --> func3_transform_item
    func3_transform_item --> func11_hidden_method
    func9_DataProcessor.hidden_method --> func0_<listcomp>
    func0_<listcomp> --> func1_stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_<listcomp> utilMethod
    class func1_stop_tracing privateMethod
    class func2_inner_calculation privateMethod
    class func3_transform_item privateMethod
    class func4_process utilMethod
    class func5_DataProcessor.init privateMethod
    class func6_init initMethod
    class func7_process_data privateMethod
    class func8_calculate_area privateMethod
    class func9_DataProcessor.hidden_method privateMethod
    class func10_DataProcessor.process utilMethod
    class func11_hidden_method privateMethod
    class func12_main_manual mainMethod
```
