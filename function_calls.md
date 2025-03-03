# Function Call Diagram

```mermaid
flowchart TD
    func10_main["system_trace.py<br>main()<br>sequence: 1<br>__return_value__: None (NoneType)"]
    func6_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>sequence: 2<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: None (NoneType)"]
    func3_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>sequence: 3<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: True (bool)"]
    func0_validate_config["system_trace.py<br>validate_config()<br>sequence: 4<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__return_value__: True (bool)"]
    func2_<genexpr>["system_trace.py<br><genexpr>()<br>sequence: 6<br>.0: <list_iterator object at 0x104eb6070> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)<br>__return_value__: None (NoneType)"]
    func8_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>sequence: 7<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)<br>__return_value__: None (NoneType)"]
    func1_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>sequence: 8<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: 'Analysis completed at 2025-03-03 15:53:34\n\n=== Detailed Results ===\nItem ID: 0\n  Value: 26\n  Processed: True\n\nItem ID: 1\n  Value: 92\n  Processed: True\n\nItem ID: 2\n  Value: 96\n  Processed: True\n\nItem ID: 3\n  Value: 92\n  Processed: True\n\nItem ID: 4\n  Value: 144\n  Processed: True\n' (str)"]
    func12_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>sequence: 9<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 26, 'processed': True}, {'id': 1, 'value': 92, 'processed': True}, {'id': 2, 'value': 96, 'processed': True}, {'id': 3, 'value': 92, 'processed': True}, {'id': 4, 'value': 144, 'processed': True}] (list)"]
    func9_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>sequence: 10<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 13}, {'id': 1, 'value': 46}, {'id': 2, 'value': 48}, {'id': 3, 'value': 46}, {'id': 4, 'value': 72}] (list)"]
    func11_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 11<br>.0: <range_iterator object at 0x104eb6b70> (range_iterator)<br>__return_value__: [{'id': 0, 'value': 13}, {'id': 1, 'value': 46}, {'id': 2, 'value': 48}, {'id': 3, 'value': 46}, {'id': 4, 'value': 72}] (list)"]
    func13_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 12<br>.0: <list_iterator object at 0x104eb6b80> (list_iterator)<br>__return_value__: [{'id': 0, 'value': 26, 'processed': True}, {'id': 1, 'value': 92, 'processed': True}, {'id': 2, 'value': 96, 'processed': True}, {'id': 3, 'value': 92, 'processed': True}, {'id': 4, 'value': 144, 'processed': True}] (list)"]
    func4_get_timestamp["system_trace.py<br>get_timestamp()<br>sequence: 13<br>__return_value__: '2025-03-03 15:53:34' (str)"]
    func5_format_results["system_trace.py<br>format_results()<br>sequence: 14<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 26, 'processed': True}, {'id': 1, 'value': 92, 'processed': True}, {'id': 2, 'value': 96, 'processed': True}, {'id': 3, 'value': 92, 'processed': True}, {'id': 4, 'value': 144, 'processed': True}] (list)<br>format_type: 'detailed' (str)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 26\n  Processed: True\n\nItem ID: 1\n  Value: 92\n  Processed: True\n\nItem ID: 2\n  Value: 96\n  Processed: True\n\nItem ID: 3\n  Value: 92\n  Processed: True\n\nItem ID: 4\n  Value: 144\n  Processed: True\n' (str)"]
    func7__detailed_format["system_trace.py<br>_detailed_format()<br>sequence: 15<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 26, 'processed': True}, {'id': 1, 'value': 92, 'processed': True}, {'id': 2, 'value': 96, 'processed': True}, {'id': 3, 'value': 92, 'processed': True}, {'id': 4, 'value': 144, 'processed': True}] (list)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 26\n  Processed: True\n\nItem ID: 1\n  Value: 92\n  Processed: True\n\nItem ID: 2\n  Value: 96\n  Processed: True\n\nItem ID: 3\n  Value: 92\n  Processed: True\n\nItem ID: 4\n  Value: 144\n  Processed: True\n' (str)"]
    func10_main -->|1->2| func6_AnalysisEngine.init
    func10_main -->|1->3| func3_AnalysisEngine.initialize
    func10_main -->|1->8| func1_AnalysisEngine.run_analysis
    func3_AnalysisEngine.initialize -->|3->4| func0_validate_config
    func3_AnalysisEngine.initialize -->|3->7| func8_DataProcessor.init
    func0_validate_config -->|4->6| func2_<genexpr>
    func1_AnalysisEngine.run_analysis -->|8->9| func12_DataProcessor.process_data
    func1_AnalysisEngine.run_analysis -->|8->13| func4_get_timestamp
    func1_AnalysisEngine.run_analysis -->|8->14| func5_format_results
    func12_DataProcessor.process_data -->|9->10| func9_DataProcessor._load_from_source
    func12_DataProcessor.process_data -->|9->12| func13_<listcomp>
    func9_DataProcessor._load_from_source -->|10->11| func11_<listcomp>
    func5_format_results -->|14->15| func7__detailed_format

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_validate_config privateMethod
    class func1_AnalysisEngine.run_analysis privateMethod
    class func2_<genexpr> utilMethod
    class func3_AnalysisEngine.initialize utilMethod
    class func4_get_timestamp privateMethod
    class func5_format_results privateMethod
    class func6_AnalysisEngine.init privateMethod
    class func7__detailed_format utilMethod
    class func8_DataProcessor.init privateMethod
    class func9_DataProcessor._load_from_source privateMethod
    class func10_main mainMethod
    class func11_<listcomp> utilMethod
    class func12_DataProcessor.process_data privateMethod
    class func13_<listcomp> utilMethod
```
