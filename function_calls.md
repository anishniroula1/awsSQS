# Function Call Diagram

```mermaid
flowchart TD
    func0_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)"]
    func1_validate_config["system_trace.py<br>validate_config()<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)"]
    func2_<genexpr>["system_trace.py<br><genexpr>()<br>.0: <list_iterator object at 0x1047211c0> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)"]
    func3_format_results["system_trace.py<br>format_results()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 194, 'processed': True}, {'id': 1, 'value': 166, 'processed': True}, {'id': 2, 'value': 18, 'processed': True}, {'id': 3, 'value': 6, 'processed': True}, {'id': 4, 'value': 194, 'processed': True}] (list)<br>format_type: 'detailed' (str)"]
    func4_main["system_trace.py<br>main()"]
    func5_get_timestamp["system_trace.py<br>get_timestamp()"]
    func6_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>__class_name__: DataProcessor (class)"]
    func7__detailed_format["system_trace.py<br>_detailed_format()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 194, 'processed': True}, {'id': 1, 'value': 166, 'processed': True}, {'id': 2, 'value': 18, 'processed': True}, {'id': 3, 'value': 6, 'processed': True}, {'id': 4, 'value': 194, 'processed': True}] (list)"]
    func8_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <range_iterator object at 0x104733390> (range_iterator)"]
    func9_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)"]
    func10_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <list_iterator object at 0x1047333a0> (list_iterator)"]
    func11_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)"]
    func12_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>__class_name__: DataProcessor (class)"]
    func13_FunctionCallTracer.stop_tracing["FunctionCallTracer.py<br>FunctionCallTracer.stop_tracing()<br>__class_name__: FunctionCallTracer (class)"]
    func14_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)"]
    func4_main --> func11_AnalysisEngine.init
    func11_AnalysisEngine.init --> func0_AnalysisEngine.initialize
    func0_AnalysisEngine.initialize --> func1_validate_config
    func1_validate_config --> func2_<genexpr>
    func2_<genexpr> --> func2_<genexpr>
    func2_<genexpr> --> func14_DataProcessor.init
    func14_DataProcessor.init --> func9_AnalysisEngine.run_analysis
    func9_AnalysisEngine.run_analysis --> func6_DataProcessor.process_data
    func6_DataProcessor.process_data --> func12_DataProcessor._load_from_source
    func12_DataProcessor._load_from_source --> func8_<listcomp>
    func8_<listcomp> --> func10_<listcomp>
    func10_<listcomp> --> func5_get_timestamp
    func5_get_timestamp --> func3_format_results
    func3_format_results --> func7__detailed_format
    func7__detailed_format --> func13_FunctionCallTracer.stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_AnalysisEngine.initialize utilMethod
    class func1_validate_config privateMethod
    class func2_<genexpr> utilMethod
    class func3_format_results privateMethod
    class func4_main mainMethod
    class func5_get_timestamp privateMethod
    class func6_DataProcessor.process_data privateMethod
    class func7__detailed_format utilMethod
    class func8_<listcomp> utilMethod
    class func9_AnalysisEngine.run_analysis privateMethod
    class func10_<listcomp> utilMethod
    class func11_AnalysisEngine.init privateMethod
    class func12_DataProcessor._load_from_source privateMethod
    class func13_FunctionCallTracer.stop_tracing privateMethod
    class func14_DataProcessor.init privateMethod
```
