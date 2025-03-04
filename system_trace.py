import random
import datetime
from typing import Dict, List, Any

from tracer import trace_and_visualize


class DataProcessor:
    def __init__(self, data_source: str, config: Dict[str, Any] = None):
        self.data_source = data_source
        self.config = config or {"default_mode": "standard"}
        self._processed_data = None
        
    def process_data(self):
        # Simulate data processing
        raw_data = self._load_from_source()
        self._processed_data = [
            {"id": item["id"], "value": item["value"] * 2, "processed": True}
            for item in raw_data
        ]
        return self._processed_data
        
    def _load_from_source(self) -> List[Dict[str, Any]]:
        # Simulate loading data from a source
        return [
            {"id": i, "value": random.randint(1, 100)}
            for i in range(5)
        ]
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Static method to validate configuration"""
        required_keys = ["default_mode"]
        return all(key in config for key in required_keys)
    
    @staticmethod
    def get_timestamp() -> str:
        """Static method to get formatted timestamp"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ResultFormatter:
    @classmethod
    def format_results(cls, results: List[Dict[str, Any]], format_type: str = "simple") -> str:
        """Class method that formats results"""
        if format_type == "simple":
            return cls._simple_format(results)
        elif format_type == "detailed":
            return cls._detailed_format(results)
        else:
            return cls._default_format(results)
    
    @classmethod
    def _simple_format(cls, results: List[Dict[str, Any]]) -> str:
        """Internal class method for simple formatting"""
        lines = ["=== Simple Results ==="]
        for item in results:
            lines.append(f"Item {item['id']}: {item['value']}")
        return "\n".join(lines)
    
    @classmethod
    def _detailed_format(cls, results: List[Dict[str, Any]]) -> str:
        """Internal class method for detailed formatting"""
        lines = ["=== Detailed Results ==="]
        for item in results:
            lines.append(f"Item ID: {item['id']}")
            lines.append(f"  Value: {item['value']}")
            for key, value in item.items():
                if key not in ["id", "value"]:
                    lines.append(f"  {key.capitalize()}: {value}")
            lines.append("")
        return "\n".join(lines)
    
    @classmethod
    def _default_format(cls, results: List[Dict[str, Any]]) -> str:
        """Internal class method for default formatting"""
        return str(results)


class AnalysisEngine:
    def __init__(self, name: str):
        self.name = name
        self.processor = None
        
    def initialize(self, data_source: str):
        """Initialize with a data processor"""
        config = {"default_mode": "standard", "created_by": self.name}
        
        # Verify config with static method
        if DataProcessor.validate_config(config):
            self.processor = DataProcessor(data_source, config)
            return True
        return False
    
    def run_analysis(self, format_type: str = "simple") -> str:
        """Run analysis and return formatted results"""
        if not self.processor:
            return "Error: Processor not initialized"
        
        # Process data
        results = self.processor.process_data()
        
        # Add timestamp using static method
        timestamp = DataProcessor.get_timestamp()
        
        # Format results using class method
        formatted_results = ResultFormatter.format_results(results, format_type)
        
        return f"Analysis completed at {timestamp}\n\n{formatted_results}"


class ConfigManager:
    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """Static method to create default configuration"""
        return {
            "default_mode": "standard",
            "created_at": datetime.datetime.now().isoformat()
        }
    
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Static method to merge configurations"""
        result = base_config.copy()
        result.update(override_config)
        return result


@trace_and_visualize(show_return=False)
def main():
    # Create analysis engine
    engine = AnalysisEngine("MainAnalyzer")
    
    # Initialize with data source
    if engine.initialize("sample_data"):
        # Run analysis with detailed formatting
        report = engine.run_analysis(format_type="detailed")
        print(report)
    else:
        print("Failed to initialize the engine")


if __name__ == "__main__":
    main()