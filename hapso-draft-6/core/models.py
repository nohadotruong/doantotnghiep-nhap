from dataclasses import dataclass, field


@dataclass
class PathResult:
    algorithm: str
    path: list[tuple[int, int]]
    metrics: dict[str, float]
    execution_time: float
    success: bool
    error_message: str = ""

    def __post_init__(self) -> None:
        if self.success:
            if not self.path:
                print("[PATHRESULT]: Error - success=True requires non-empty path")
            if not self.metrics:
                print("[PATHRESULT]: Error - success=True requires metrics dict")
        if self.execution_time < 0.0:
            print("[PATHRESULT]: Error - execution_time cannot be negative")


@dataclass
class SimulationResult:
    algorithm: str
    path_result: PathResult
    timestamp: float = 0.0


@dataclass
class ComparisonMetrics:
    algorithm_results: dict[str, PathResult] = field(default_factory=dict)
    generation_timestamp: float = 0.0

    def add_result(self, result: PathResult) -> None:
        self.algorithm_results[result.algorithm] = result

    def get_algorithms(self) -> list[str]:
        return sorted(self.algorithm_results.keys())

    def get_result(self, algorithm: str) -> PathResult | None:
        return self.algorithm_results.get(algorithm)
