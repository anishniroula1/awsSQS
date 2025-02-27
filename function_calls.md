# Function Call Diagram

```mermaid
flowchart TD
    func0__detailed_format["system_trace.py<br>_detailed_format()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 136, 'processed': True}, {'id': 1, 'value': 24, 'processed': True}, {'id': 2, 'value': 122, 'processed': True}, {'id': 3, 'value': 28, 'processed': True}, {'id': 4, 'value': 134, 'processed': True}] (list)"]
    func1_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)"]
    func2_main["system_trace.py<br>main()"]
    func3_get_timestamp["system_trace.py<br>get_timestamp()"]
    func4_format_results["system_trace.py<br>format_results()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 136, 'processed': True}, {'id': 1, 'value': 24, 'processed': True}, {'id': 2, 'value': 122, 'processed': True}, {'id': 3, 'value': 28, 'processed': True}, {'id': 4, 'value': 134, 'processed': True}] (list)<br>format_type: 'detailed' (str)"]
    func5_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)"]
    func6_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>__class_name__: DataProcessor (class)"]
    func7_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <list_iterator object at 0x100cd4520> (list_iterator)"]
    func8_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)"]
    func9_FunctionCallTracer.stop_tracing["FunctionCallTracer.py<br>FunctionCallTracer.stop_tracing()<br>__class_name__: FunctionCallTracer (class)"]
    func10_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>__class_name__: DataProcessor (class)"]
    func11_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <range_iterator object at 0x100cd4510> (range_iterator)"]
    func12_<genexpr>["system_trace.py<br><genexpr>()<br>.0: <list_iterator object at 0x100cd4580> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)"]
    func13_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)"]
    func14_validate_config["system_trace.py<br>validate_config()<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)"]
    func2_main --> func13_AnalysisEngine.init
    func13_AnalysisEngine.init --> func1_AnalysisEngine.initialize
    func1_AnalysisEngine.initialize --> func14_validate_config
    func14_validate_config --> func12_<genexpr>
    func12_<genexpr> --> func12_<genexpr>
    func12_<genexpr> --> func8_DataProcessor.init
    func8_DataProcessor.init --> func5_AnalysisEngine.run_analysis
    func5_AnalysisEngine.run_analysis --> func6_DataProcessor.process_data
    func6_DataProcessor.process_data --> func10_DataProcessor._load_from_source
    func10_DataProcessor._load_from_source --> func11_<listcomp>
    func11_<listcomp> --> func7_<listcomp>
    func7_<listcomp> --> func3_get_timestamp
    func3_get_timestamp --> func4_format_results
    func4_format_results --> func0__detailed_format
    func0__detailed_format --> func9_FunctionCallTracer.stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0__detailed_format utilMethod
    class func1_AnalysisEngine.initialize utilMethod
    class func2_main mainMethod
    class func3_get_timestamp privateMethod
    class func4_format_results privateMethod
    class func5_AnalysisEngine.run_analysis privateMethod
    class func6_DataProcessor.process_data privateMethod
    class func7_<listcomp> utilMethod
    class func8_DataProcessor.init privateMethod
    class func9_FunctionCallTracer.stop_tracing privateMethod
    class func10_DataProcessor._load_from_source privateMethod
    class func11_<listcomp> utilMethod
    class func12_<genexpr> utilMethod
    class func13_AnalysisEngine.init privateMethod
    class func14_validate_config privateMethod
```
