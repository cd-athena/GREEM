from dataclasses import dataclass, field
import json
import yaml

@dataclass
class BenchmarkMetadata:

    config_files: list[str]
    cuda_enabled: bool
    idle_time_csv_path: str
    benchmark_result_csv_path: str


    def to_json(self, file_path: str = None) -> dict:
        pass
