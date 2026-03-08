from src.analysis.engine import AnalysisEngine
from src.analysis.sample_data import sample_trades


def test_analysis_engine_returns_findings() -> None:
    results = AnalysisEngine().run(sample_trades())
    assert len(results) >= 1
    assert any(result.pattern for result in results)
