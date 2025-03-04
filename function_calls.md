# Function Call Diagram

```mermaid
flowchart TD
    func0__detailed_format["system_trace.py<br>_detailed_format()<br>sequence: 15<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 96, 'processed': True}, {'id': 1, 'value': 54, 'processed': True}, {'id': 2, 'value': 20, 'processed': True}, {'id': 3, 'value': 152, 'processed': True}, {'id': 4, 'value': 110, 'processed': True}] (list)"]
    func1_AnalysisEngine.initialize["system_trace.py<br>AnalysisEngine.initialize()<br>sequence: 3<br>data_source: 'sample_data' (str)"]
    func2_DataProcessor.process_data["system_trace.py<br>DataProcessor.process_data()<br>sequence: 9"]
    func3_DataProcessor.init["system_trace.py<br>DataProcessor.__init__()<br>sequence: 7<br>data_source: 'sample_data' (str)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)"]
    func4_DataProcessor._load_from_source["system_trace.py<br>DataProcessor._load_from_source()<br>sequence: 10"]
    func5_get_timestamp["system_trace.py<br>get_timestamp()<br>sequence: 13"]
    func6_validate_config["system_trace.py<br>validate_config()<br>sequence: 4<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)"]
    func7_AnalysisEngine.init["system_trace.py<br>AnalysisEngine.__init__()<br>sequence: 2<br>name: 'MainAnalyzer' (str)"]
    func8_main["system_trace.py<br>main()<br>sequence: 1"]
    func9_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 12<br>.0: <list_iterator object at 0x100803550> (list_iterator)"]
    func10_AnalysisEngine.run_analysis["system_trace.py<br>AnalysisEngine.run_analysis()<br>sequence: 8<br>format_type: 'detailed' (str)"]
    func11_format_results["system_trace.py<br>format_results()<br>sequence: 14<br>cls: <class '__main__.ResultFormatter'> (type)<br>results: [{'id': 0, 'value': 96, 'processed': True}, {'id': 1, 'value': 54, 'processed': True}, {'id': 2, 'value': 20, 'processed': True}, {'id': 3, 'value': 152, 'processed': True}, {'id': 4, 'value': 110, 'processed': True}] (list)<br>format_type: 'detailed' (str)"]
    func12_<listcomp>["system_trace.py<br><listcomp>()<br>sequence: 11<br>.0: <range_iterator object at 0x100803540> (range_iterator)"]
    func13_<genexpr>["system_trace.py<br><genexpr>()<br>sequence: 6<br>.0: <list_iterator object at 0x1008035b0> (list_iterator)<br>config: {'default_mode': 'standard', 'created_by': 'MainAnalyzer'} (dict)<br>key: 'default_mode' (str)"]
    func8_main -->|1→2| func7_AnalysisEngine.init
    func8_main -->|1→3| func1_AnalysisEngine.initialize
    func8_main -->|1→8| func10_AnalysisEngine.run_analysis
    func1_AnalysisEngine.initialize -->|3→4| func6_validate_config
    func1_AnalysisEngine.initialize -->|3→7| func3_DataProcessor.init
    func6_validate_config -->|4→6| func13_<genexpr>
    func10_AnalysisEngine.run_analysis -->|8→9| func2_DataProcessor.process_data
    func10_AnalysisEngine.run_analysis -->|8→13| func5_get_timestamp
    func10_AnalysisEngine.run_analysis -->|8→14| func11_format_results
    func2_DataProcessor.process_data -->|9→10| func4_DataProcessor._load_from_source
    func2_DataProcessor.process_data -->|9→12| func9_<listcomp>
    func4_DataProcessor._load_from_source -->|10→11| func12_<listcomp>
    func11_format_results -->|14→15| func0__detailed_format

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef mainMethod fill:#d4e5ff,stroke:#4285f4,stroke-width:2px
    classDef utilMethod fill:#e6f4ea,stroke:#34a853,stroke-width:1px
    classDef privateMethod fill:#fef7e0,stroke:#fbbc05,stroke-width:1px
    classDef initMethod fill:#fce8e6,stroke:#ea4335,stroke-width:1px
    class func0__detailed_format utilMethod
    class func1_AnalysisEngine.initialize utilMethod
    class func2_DataProcessor.process_data privateMethod
    class func3_DataProcessor.init privateMethod
    class func4_DataProcessor._load_from_source privateMethod
    class func5_get_timestamp privateMethod
    class func6_validate_config privateMethod
    class func7_AnalysisEngine.init privateMethod
    class func8_main mainMethod
    class func9_<listcomp> utilMethod
    class func10_AnalysisEngine.run_analysis privateMethod
    class func11_format_results privateMethod
    class func12_<listcomp> utilMethod
    class func13_<genexpr> utilMethod
```
