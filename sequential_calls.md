# Function Call Diagram

```mermaid
flowchart TD
    func4_main["system_trace.py<br>main()<br>sequence: 1<br>__return_value__: None (NoneType)"]
    func13_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>sequence: 2<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: None (NoneType)"]
    func11_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>sequence: 3<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: True (bool)"]
    func5_validate_config["system_trace.py<br>validate_config()<br>sequence: 4<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__return_value__: True (bool)"]
    func1_<genexpr>["system_trace.py<br><genexpr>()<br>sequence: 6<br>.0: <list_iterator object at 0x104b81700> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)<br>__return_value__: None (NoneType)"]
    func3_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>sequence: 7<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)<br>__return_value__: None (NoneType)"]
    func8_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>sequence: 8<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: 'Analysis completed at 2025-03-03 15:56:36\n\n=== Detailed Results ===\nItem ID: 0\n  Value: 188\n  Processed: True\n\nItem ID: 1\n  Value: 28\n  Processed: True\n\nItem ID: 2\n  Value: 118\n  Processed: True\n\nItem ID: 3\n  Value: 10\n  Processed: True\n\nItem ID: 4\n  Value: 104\n  Processed: True\n' (str)"]
    func6_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>sequence: 9<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 188, 'processed': True}, {'id': 1, 'value': 28, 'processed': True}, {'id': 2, 'value': 118, 'processed': True}, {'id': 3, 'value': 10, 'processed': True}, {'id': 4, 'value': 104, 'processed': True}] (list)"]
    func0_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>sequence: 10<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 94}, {'id': 1, 'value': 14}, {'id': 2, 'value': 59}, {'id': 3, 'value': 5}, {'id': 4, 'value': 52}] (list)"]
    func10_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 11<br>.0: <range_iterator object at 0x104b928d0> (range_iterator)<br>__return_value__: [{'id': 0, 'value': 94}, {'id': 1, 'value': 14}, {'id': 2, 'value': 59}, {'id': 3, 'value': 5}, {'id': 4, 'value': 52}] (list)"]
    func7_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 12<br>.0: <list_iterator object at 0x104b928e0> (list_iterator)<br>__return_value__: [{'id': 0, 'value': 188, 'processed': True}, {'id': 1, 'value': 28, 'processed': True}, {'id': 2, 'value': 118, 'processed': True}, {'id': 3, 'value': 10, 'processed': True}, {'id': 4, 'value': 104, 'processed': True}] (list)"]
    func9_get_timestamp["system_trace.py<br>get_timestamp()<br>sequence: 13<br>__return_value__: '2025-03-03 15:56:36' (str)"]
    func12_format_results["system_trace.py<br>format_results()<br>sequence: 14<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 188, 'processed': True}, {'id': 1, 'value': 28, 'processed': True}, {'id': 2, 'value': 118, 'processed': True}, {'id': 3, 'value': 10, 'processed': True}, {'id': 4, 'value': 104, 'processed': True}] (list)<br>format_type: 'detailed' (str)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 188\n  Processed: True\n\nItem ID: 1\n  Value: 28\n  Processed: True\n\nItem ID: 2\n  Value: 118\n  Processed: True\n\nItem ID: 3\n  Value: 10\n  Processed: True\n\nItem ID: 4\n  Value: 104\n  Processed: True\n' (str)"]
    func2__detailed_format["system_trace.py<br>_detailed_format()<br>sequence: 15<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 188, 'processed': True}, {'id': 1, 'value': 28, 'processed': True}, {'id': 2, 'value': 118, 'processed': True}, {'id': 3, 'value': 10, 'processed': True}, {'id': 4, 'value': 104, 'processed': True}] (list)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 188\n  Processed: True\n\nItem ID: 1\n  Value: 28\n  Processed: True\n\nItem ID: 2\n  Value: 118\n  Processed: True\n\nItem ID: 3\n  Value: 10\n  Processed: True\n\nItem ID: 4\n  Value: 104\n  Processed: True\n' (str)"]
    func4_main -->|1->2| func13_AnalysisEngine.init
    func4_main -->|1->3| func11_AnalysisEngine.initialize
    func4_main -->|1->8| func8_AnalysisEngine.run_analysis
    func11_AnalysisEngine.initialize -->|3->4| func5_validate_config
    func11_AnalysisEngine.initialize -->|3->7| func3_DataProcessor.init
    func5_validate_config -->|4->6| func1_<genexpr>
    func8_AnalysisEngine.run_analysis -->|8->9| func6_DataProcessor.process_data
    func8_AnalysisEngine.run_analysis -->|8->13| func9_get_timestamp
    func8_AnalysisEngine.run_analysis -->|8->14| func12_format_results
    func6_DataProcessor.process_data -->|9->10| func0_DataProcessor._load_from_source
    func6_DataProcessor.process_data -->|9->12| func7_<listcomp>
    func0_DataProcessor._load_from_source -->|10->11| func10_<listcomp>
    func12_format_results -->|14->15| func2__detailed_format

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_DataProcessor._load_from_source privateMethod
    class func1_<genexpr> utilMethod
    class func2__detailed_format utilMethod
    class func3_DataProcessor.init privateMethod
    class func4_main mainMethod
    class func5_validate_config privateMethod
    class func6_DataProcessor.process_data privateMethod
    class func7_<listcomp> utilMethod
    class func8_AnalysisEngine.run_analysis privateMethod
    class func9_get_timestamp privateMethod
    class func10_<listcomp> utilMethod
    class func11_AnalysisEngine.initialize utilMethod
    class func12_format_results privateMethod
    class func13_AnalysisEngine.init privateMethod
```
