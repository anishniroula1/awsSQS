# Function Call Diagram

```mermaid
flowchart TD
    func0_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <list_iterator object at 0x1049954c0> (list_iterator)"]
    func1_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)"]
    func2_main["system_trace.py<br>main()"]
    func3_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)"]
    func4_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <range_iterator object at 0x1049954b0> (range_iterator)"]
    func5_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>__class_name__: DataProcessor (class)"]
    func6_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)"]
    func7__detailed_format["system_trace.py<br>_detailed_format()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 118, 'processed': True}, {'id': 1, 'value': 188, 'processed': True}, {'id': 2, 'value': 196, 'processed': True}, {'id': 3, 'value': 198, 'processed': True}, {'id': 4, 'value': 126, 'processed': True}] (list)"]
    func8_<genexpr>["system_trace.py<br><genexpr>()<br>.0: <list_iterator object at 0x104995520> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)"]
    func9_validate_config["system_trace.py<br>validate_config()<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)"]
    func10_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>__class_name__: DataProcessor (class)"]
    func11_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)"]
    func12_get_timestamp["system_trace.py<br>get_timestamp()"]
    func13_format_results["system_trace.py<br>format_results()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 118, 'processed': True}, {'id': 1, 'value': 188, 'processed': True}, {'id': 2, 'value': 196, 'processed': True}, {'id': 3, 'value': 198, 'processed': True}, {'id': 4, 'value': 126, 'processed': True}] (list)<br>format_type: 'detailed' (str)"]
    func14_FunctionCallTracer.stop_tracing["FunctionCallTracer.py<br>FunctionCallTracer.stop_tracing()<br>__class_name__: FunctionCallTracer (class)"]
    func2_main --> func3_AnalysisEngine.init
    func3_AnalysisEngine.init --> func11_AnalysisEngine.initialize
    func11_AnalysisEngine.initialize --> func9_validate_config
    func9_validate_config --> func8_<genexpr>
    func8_<genexpr> --> func8_<genexpr>
    func8_<genexpr> --> func1_DataProcessor.init
    func1_DataProcessor.init --> func6_AnalysisEngine.run_analysis
    func6_AnalysisEngine.run_analysis --> func10_DataProcessor.process_data
    func10_DataProcessor.process_data --> func5_DataProcessor._load_from_source
    func5_DataProcessor._load_from_source --> func4_<listcomp>
    func4_<listcomp> --> func0_<listcomp>
    func0_<listcomp> --> func12_get_timestamp
    func12_get_timestamp --> func13_format_results
    func13_format_results --> func7__detailed_format
    func7__detailed_format --> func14_FunctionCallTracer.stop_tracing

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_<listcomp> utilMethod
    class func1_DataProcessor.init privateMethod
    class func2_main mainMethod
    class func3_AnalysisEngine.init privateMethod
    class func4_<listcomp> utilMethod
    class func5_DataProcessor._load_from_source privateMethod
    class func6_AnalysisEngine.run_analysis privateMethod
    class func7__detailed_format utilMethod
    class func8_<genexpr> utilMethod
    class func9_validate_config privateMethod
    class func10_DataProcessor.process_data privateMethod
    class func11_AnalysisEngine.initialize utilMethod
    class func12_get_timestamp privateMethod
    class func13_format_results privateMethod
    class func14_FunctionCallTracer.stop_tracing privateMethod
```
