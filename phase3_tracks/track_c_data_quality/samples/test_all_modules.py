"""모든 모듈 통합 테스트"""
import pandas as pd
import numpy as np

print("=" * 60)
print("DATA QUALITY AGENT - Comprehensive Test")
print("=" * 60)

# 샘플 데이터 생성
np.random.seed(42)
df = pd.DataFrame({
    'id': range(1, 101),
    'email': ['user' + str(i) + '@example.com' if i % 10 != 0 else 'invalid' for i in range(100)],
    'age': list(np.random.normal(35, 10, 98).astype(int)) + [200, -5],
    'salary': list(np.random.normal(50000, 15000, 96).astype(int)) + [0, -5000, 500000, 600000],
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

print("\n1. Testing Quality Profiler...")
try:
    from quality_profiler import QualityProfiler
    profiler = QualityProfiler()
    score = profiler.calculate_quality_score(df)
    print(f"   ✓ Quality Score: {score.overall_score:.2%}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n2. Testing Rule Validator...")
try:
    from rule_validator import RuleValidator, CompletenessRule, UniquenessRule
    validator = RuleValidator()
    validator.add_rule(CompletenessRule('email', null_threshold=0.05))
    validator.add_rule(UniquenessRule('id'))
    results = validator.validate(df)
    print(f"   ✓ Validated {len(results)} columns")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n3. Testing Anomaly Detector...")
try:
    from anomaly_detector import AnomalyDetector
    detector = AnomalyDetector(contamination=0.05)
    result = detector.zscore_detection(df['age'].dropna(), threshold=2.5)
    print(f"   ✓ Detected {result.anomaly_count} anomalies")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n4. Testing Semantic Checker...")
try:
    from semantic_checker import LLMSemanticChecker
    checker = LLMSemanticChecker(mock_mode=True)
    result = checker.check_semantic_consistency(df, 'email')
    print(f"   ✓ Semantic check completed (valid: {result.is_valid})")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n5. Testing Alert Manager...")
try:
    from alert_manager import AlertManager, AlertLevel, AlertChannel, LogAlertProvider
    manager = AlertManager()
    manager.register_provider(AlertChannel.LOG, LogAlertProvider())
    manager.send_quality_alert('test', 0.65, 0.75, channels=[AlertChannel.LOG])
    print(f"   ✓ Alert system working")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n6. Testing Quality Dashboard...")
try:
    from quality_dashboard import QualityDashboard
    dashboard = QualityDashboard()
    dashboard.add_metrics(pd.Timestamp.now(), 0.75, 0.8, 0.7, 0.75, 0.8)
    cards = dashboard.create_summary_cards()
    print(f"   ✓ Dashboard initialized")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n7. Testing Data Quality Agent...")
try:
    from data_quality_agent import DataQualityAgent
    agent = DataQualityAgent()
    state = agent.execute(df)
    print(f"   ✓ Agent execution completed (quality: {state.overall_quality_score:.2%})")
    print(f"   ✓ Issues found: {len(state.issues)}")
    print(f"   ✓ Recommendations: {len(state.recommendations)}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:50]}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
