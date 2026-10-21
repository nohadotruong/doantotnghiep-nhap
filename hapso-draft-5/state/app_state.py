
from core.models import ComparisonMetrics, PathResult
from dataclasses import dataclass, field
from map.grid_map import GridMap
from typing import Optional


@dataclass
class AppState:

    # Current map being edited/simulated
    current_map: Optional[GridMap] = None

    # Current page (F1, F2, F3)
    current_page: str = "F1"  # "F1" (editor), "F2" (simulation), "F3" (comparison)

    # F2 Simulation Results - dict mapping algorithm name to its PathResult
    f2_results: dict[str, PathResult] = field(default_factory=dict)

    # F3 Comparison Results - multiple algorithm results with metrics
    f3_comparison_results: Optional[ComparisonMetrics] = None

    def reset(self) -> None:
        self.current_map = None
        self.current_page = "F1"
        self.f2_results = {}
        self.f3_comparison_results = None

    def clear_f2_results(self) -> None:
        self.f2_results = {}

    def add_f2_result(self, algorithm_name: str, result: PathResult) -> None:
        self.f2_results[algorithm_name] = result

    def get_f2_result(self, algorithm_name: str) -> Optional[PathResult]:
        return self.f2_results.get(algorithm_name)

    def has_f2_results(self) -> bool:
        return len(self.f2_results) > 0

    def set_f3_comparison(self, comparison: ComparisonMetrics) -> None:
        self.f3_comparison_results = comparison

    def get_f3_comparison(self) -> Optional[ComparisonMetrics]:
        return self.f3_comparison_results

    def has_f3_comparison(self) -> bool:
        return self.f3_comparison_results is not None


# Global singleton instance
_app_state: Optional[AppState] = None


def get_app_state() -> AppState:
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


def reset_app_state() -> None:
    global _app_state
    if _app_state is not None:
        _app_state.reset()
