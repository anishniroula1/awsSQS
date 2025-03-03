# Function Call Diagram

```mermaid
flowchart TD
    func0_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <list_iterator object at 0x1027c7310> (list_iterator)<br>__return_value__: [{'id': 0, 'value': 76, 'processed': True}, {'id': 1, 'value': 26, 'processed': True}, {'id': 2, 'value': 8, 'processed': True}, {'id': 3, 'value': 56, 'processed': True}, {'id': 4, 'value': 102, 'processed': True}] (list)"]
    func1_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 38}, {'id': 1, 'value': 13}, {'id': 2, 'value': 4}, {'id': 3, 'value': 28}, {'id': 4, 'value': 51}] (list)"]
    func2_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>data_source: 'sample_data' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: True (bool)"]
    func3_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__class_name__: DataProcessor (class)<br>__return_value__: None (NoneType)"]
    func4_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>__class_name__: DataProcessor (class)<br>__return_value__: [{'id': 0, 'value': 76, 'processed': True}, {'id': 1, 'value': 26, 'processed': True}, {'id': 2, 'value': 8, 'processed': True}, {'id': 3, 'value': 56, 'processed': True}, {'id': 4, 'value': 102, 'processed': True}] (list)"]
    func5_format_results["system_trace.py<br>format_results()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 76, 'processed': True}, {'id': 1, 'value': 26, 'processed': True}, {'id': 2, 'value': 8, 'processed': True}, {'id': 3, 'value': 56, 'processed': True}, {'id': 4, 'value': 102, 'processed': True}] (list)<br>format_type: 'detailed' (str)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 76\n  Processed: True\n\nItem ID: 1\n  Value: 26\n  Processed: True\n\nItem ID: 2\n  Value: 8\n  Processed: True\n\nItem ID: 3\n  Value: 56\n  Processed: True\n\nItem ID: 4\n  Value: 102\n  Processed: True\n' (str)"]
    func6_<genexpr>["system_trace.py<br><genexpr>()<br>.0: <list_iterator object at 0x1027b5130> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)<br>__return_value__: None (NoneType)"]
    func7_validate_config["system_trace.py<br>validate_config()<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>__return_value__: True (bool)"]
    func8_main["system_trace.py<br>main()<br>__return_value__: None (NoneType)"]
    func9_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>format_type: 'detailed' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: 'Analysis completed at 2025-03-03 11:06:35\n\n=== Detailed Results ===\nItem ID: 0\n  Value: 76\n  Processed: True\n\nItem ID: 1\n  Value: 26\n  Processed: True\n\nItem ID: 2\n  Value: 8\n  Processed: True\n\nItem ID: 3\n  Value: 56\n  Processed: True\n\nItem ID: 4\n  Value: 102\n  Processed: True\n' (str)"]
    func10__detailed_format["system_trace.py<br>_detailed_format()<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 76, 'processed': True}, {'id': 1, 'value': 26, 'processed': True}, {'id': 2, 'value': 8, 'processed': True}, {'id': 3, 'value': 56, 'processed': True}, {'id': 4, 'value': 102, 'processed': True}] (list)<br>__return_value__: '=== Detailed Results ===\nItem ID: 0\n  Value: 76\n  Processed: True\n\nItem ID: 1\n  Value: 26\n  Processed: True\n\nItem ID: 2\n  Value: 8\n  Processed: True\n\nItem ID: 3\n  Value: 56\n  Processed: True\n\nItem ID: 4\n  Value: 102\n  Processed: True\n' (str)"]
    func11_get_timestamp["system_trace.py<br>get_timestamp()<br>__return_value__: '2025-03-03 11:06:35' (str)"]
    func12_<listcomp>["system_trace.py<br><listcomp>()<br>.0: <range_iterator object at 0x1027c7300> (range_iterator)<br>__return_value__: [{'id': 0, 'value': 38}, {'id': 1, 'value': 13}, {'id': 2, 'value': 4}, {'id': 3, 'value': 28}, {'id': 4, 'value': 51}] (list)"]
    func13_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>name: 'MainAnalyzer' (str)<br>__class_name__: AnalysisEngine (class)<br>__return_value__: None (NoneType)"]
    func8_main --> func13_AnalysisEngine.init
    func8_main --> func2_AnalysisEngine.initialize
    func8_main --> func9_AnalysisEngine.run_analysis
    func2_AnalysisEngine.initialize --> func7_validate_config
    func2_AnalysisEngine.initialize --> func3_DataProcessor.init
    func7_validate_config --> func6_<genexpr>
    func9_AnalysisEngine.run_analysis --> func4_DataProcessor.process_data
    func9_AnalysisEngine.run_analysis --> func11_get_timestamp
    func9_AnalysisEngine.run_analysis --> func5_format_results
    func4_DataProcessor.process_data --> func1_DataProcessor._load_from_source
    func4_DataProcessor.process_data --> func0_<listcomp>
    func1_DataProcessor._load_from_source --> func12_<listcomp>
    func5_format_results --> func10__detailed_format

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0_<listcomp> utilMethod
    class func1_DataProcessor._load_from_source privateMethod
    class func2_AnalysisEngine.initialize utilMethod
    class func3_DataProcessor.init privateMethod
    class func4_DataProcessor.process_data privateMethod
    class func5_format_results privateMethod
    class func6_<genexpr> utilMethod
    class func7_validate_config privateMethod
    class func8_main mainMethod
    class func9_AnalysisEngine.run_analysis privateMethod
    class func10__detailed_format utilMethod
    class func11_get_timestamp privateMethod
    class func12_<listcomp> utilMethod
    class func13_AnalysisEngine.init privateMethod
```
