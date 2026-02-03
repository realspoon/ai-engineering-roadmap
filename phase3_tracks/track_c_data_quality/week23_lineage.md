# Week 23: 데이터 리니지 분석 (Data Lineage & Impact Analysis)

## 학습 목표
- 데이터 리니지 개념 이해
- 영향 분석 (Impact Analysis) 구현
- 자동 리니지 추적 시스템 구축

## 1. 데이터 리니지의 개념

### 1.1 정의
데이터가 소스에서 최종 목적지까지 어떻게 흐르는지 추적하는 프로세스

### 1.2 리니지의 구성 요소
```
┌─────────────────────────────────────┐
│   Source (원본 데이터)              │
│   - Database tables                 │
│   - APIs                            │
│   - Files                           │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│   Transformations (변환)             │
│   - ETL processes                   │
│   - Data pipelines                  │
│   - Calculations                    │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│   Intermediate Tables (중간 결과)    │
│   - Staging tables                  │
│   - Aggregations                    │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│   Target (최종 데이터)              │
│   - Data warehouse                  │
│   - Reports                         │
│   - Dashboards                      │
└─────────────────────────────────────┘
```

### 1.3 리니지의 종류

```
1. Column-level Lineage
   어느 컬럼이 어느 컬럼에서 파생되었는가?

2. Table-level Lineage
   어느 테이블이 어느 테이블의 데이터를 사용하는가?

3. Process-level Lineage
   어떤 ETL/프로세스가 데이터를 변환하는가?

4. Business-level Lineage
   데이터가 비즈니스 목표와 어떻게 연결되어 있는가?
```

## 2. 리니지 추적 시스템 구축

### 2.1 메타데이터 수집
```python
import json
from datetime import datetime
from typing import Dict, List, Set

class DataLineageTracker:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.lineage_graph = {}  # DAG 구조
        self.metadata_store = {}
        self.transformations = {}

    def register_source(self, source_id: str, source_type: str,
                       location: str, schema: Dict):
        """데이터 소스 등록"""
        self.metadata_store[source_id] = {
            'type': source_type,  # database, api, file
            'location': location,
            'schema': schema,
            'registered_at': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }

        # 리니지 그래프에 노드 추가
        if source_id not in self.lineage_graph:
            self.lineage_graph[source_id] = {
                'id': source_id,
                'type': 'SOURCE',
                'parents': [],
                'children': [],
                'metadata': self.metadata_store[source_id]
            }

    def register_transformation(self, transform_id: str,
                               source_ids: List[str],
                               target_id: str,
                               transform_logic: str,
                               transform_type: str = 'SQL'):
        """변환 프로세스 등록"""
        self.transformations[transform_id] = {
            'id': transform_id,
            'sources': source_ids,
            'target': target_id,
            'logic': transform_logic,
            'type': transform_type,
            'registered_at': datetime.now().isoformat()
        }

        # 리니지 그래프 업데이트
        for source_id in source_ids:
            if source_id in self.lineage_graph:
                self.lineage_graph[source_id]['children'].append(transform_id)

        if target_id not in self.lineage_graph:
            self.lineage_graph[target_id] = {
                'id': target_id,
                'type': 'TRANSFORMED',
                'parents': source_ids,
                'children': [],
                'transformation': transform_id,
                'metadata': {}
            }
        else:
            self.lineage_graph[target_id]['parents'] = source_ids

    def register_target(self, target_id: str, target_type: str,
                       location: str, source_ids: List[str]):
        """타겟 데이터셋 등록"""
        self.metadata_store[target_id] = {
            'type': target_type,  # report, dashboard, table
            'location': location,
            'sources': source_ids,
            'registered_at': datetime.now().isoformat()
        }

        # 리니지 그래프에 노드 추가
        if target_id not in self.lineage_graph:
            self.lineage_graph[target_id] = {
                'id': target_id,
                'type': 'TARGET',
                'parents': source_ids,
                'children': [],
                'metadata': self.metadata_store[target_id]
            }

    def get_lineage(self, node_id: str, direction: str = 'both') -> Dict:
        """리니지 조회"""
        if node_id not in self.lineage_graph:
            return None

        lineage = {
            'node': self.lineage_graph[node_id],
            'upstream': [],
            'downstream': []
        }

        if direction in ['upstream', 'both']:
            lineage['upstream'] = self._get_upstream(node_id)

        if direction in ['downstream', 'both']:
            lineage['downstream'] = self._get_downstream(node_id)

        return lineage

    def _get_upstream(self, node_id: str, visited: Set = None) -> List:
        """상위 노드 조회 (재귀)"""
        if visited is None:
            visited = set()

        if node_id in visited:
            return []

        visited.add(node_id)
        upstream = []

        node = self.lineage_graph.get(node_id)
        if not node:
            return upstream

        for parent_id in node.get('parents', []):
            upstream.append({
                'id': parent_id,
                'node': self.lineage_graph.get(parent_id)
            })
            # 재귀적으로 상위 노드 추가
            upstream.extend(
                self._get_upstream(parent_id, visited)
            )

        return upstream

    def _get_downstream(self, node_id: str, visited: Set = None) -> List:
        """하위 노드 조회 (재귀)"""
        if visited is None:
            visited = set()

        if node_id in visited:
            return []

        visited.add(node_id)
        downstream = []

        node = self.lineage_graph.get(node_id)
        if not node:
            return downstream

        for child_id in node.get('children', []):
            downstream.append({
                'id': child_id,
                'node': self.lineage_graph.get(child_id)
            })
            # 재귀적으로 하위 노드 추가
            downstream.extend(
                self._get_downstream(child_id, visited)
            )

        return downstream
```

## 3. Column-Level Lineage

### 3.1 컬럼 레벨 리니지 추적
```python
class ColumnLineageTracker:
    def __init__(self):
        self.column_lineage = {}  # source_col -> target_cols 매핑

    def extract_column_lineage_from_sql(self, sql_query: str,
                                       source_table: str,
                                       target_table: str):
        """SQL 쿼리에서 컬럼 리니지 추출"""
        import sqlparse
        from sqlparse.sql import IdentifierList, Identifier, Where

        parsed = sqlparse.parse(sql_query)[0]

        # SELECT 절 추출
        select_tokens = self._extract_select_tokens(parsed)

        # FROM 절 추출
        from_tables = self._extract_from_tables(parsed)

        # WHERE 절에서 조건 컬럼 추출
        where_columns = self._extract_where_columns(parsed)

        # 컬럼 매핑 생성
        for target_col, source_col in select_tokens:
            if source_col not in self.column_lineage:
                self.column_lineage[source_col] = []

            self.column_lineage[source_col].append({
                'source_table': source_table,
                'target_table': target_table,
                'target_column': target_col,
                'transformation': 'DIRECT' if source_col == target_col else 'CALCULATED',
                'dependencies': where_columns
            })

        return self.column_lineage

    def extract_column_lineage_from_code(self, code: str,
                                        source_var: str,
                                        target_var: str):
        """Python 코드에서 컬럼 리니지 추출"""
        import ast

        tree = ast.parse(code)
        assignments = {}

        # 변수 할당 추적
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = node.value

        # 계산 관계 추출
        lineage = self._extract_dependencies(
            assignments, source_var, target_var
        )

        return lineage

    def _extract_select_tokens(self, parsed):
        """SELECT 절에서 컬럼 추출"""
        select_cols = []
        # 복잡한 파싱 로직
        return select_cols

    def _extract_from_tables(self, parsed):
        """FROM 절에서 테이블 추출"""
        tables = []
        # 테이블 추출 로직
        return tables

    def _extract_where_columns(self, parsed):
        """WHERE 절에서 컬럼 추출"""
        columns = []
        # WHERE 조건 컬럼 추출 로직
        return columns

    def _extract_dependencies(self, assignments, source, target):
        """의존성 추출"""
        dependencies = {}
        # 계산 관계 추출 로직
        return dependencies

    def get_column_lineage(self, column_id: str) -> Dict:
        """특정 컬럼의 리니지 조회"""
        return self.column_lineage.get(column_id, [])
```

## 4. 영향 분석 (Impact Analysis)

### 4.1 데이터 변경의 영향도 분석
```python
class ImpactAnalysisEngine:
    def __init__(self, lineage_tracker):
        self.lineage = lineage_tracker
        self.impact_cache = {}

    def analyze_impact(self, changed_node_id: str,
                      change_type: str = 'SCHEMA_CHANGE') -> Dict:
        """데이터 변경의 영향도 분석"""
        impacts = {
            'changed_node': changed_node_id,
            'change_type': change_type,
            'affected_nodes': [],
            'affected_reports': [],
            'affected_dashboards': [],
            'risk_level': 'LOW',
            'recommendations': []
        }

        # 1. 직접 영향받는 노드
        directly_affected = self._find_directly_affected(
            changed_node_id
        )
        impacts['affected_nodes'].extend(directly_affected)

        # 2. 간접 영향받는 노드
        indirectly_affected = self._find_indirectly_affected(
            directly_affected
        )
        impacts['affected_nodes'].extend(indirectly_affected)

        # 3. 영향받는 리포트/대시보드
        for node in impacts['affected_nodes']:
            if self._is_report(node):
                impacts['affected_reports'].append(node)
            elif self._is_dashboard(node):
                impacts['affected_dashboards'].append(node)

        # 4. 위험도 평가
        impacts['risk_level'] = self._assess_risk(
            impacts['affected_nodes'],
            change_type
        )

        # 5. 권장사항 생성
        impacts['recommendations'] = self._generate_recommendations(
            impacts, change_type
        )

        return impacts

    def _find_directly_affected(self, node_id: str) -> List[str]:
        """직접 영향받는 노드"""
        lineage = self.lineage.get_lineage(node_id, direction='downstream')
        return [child['id'] for child in lineage.get('downstream', [])]

    def _find_indirectly_affected(self, directly_affected: List[str]) -> List[str]:
        """간접 영향받는 노드"""
        indirectly = []
        for node_id in directly_affected:
            lineage = self.lineage.get_lineage(node_id, direction='downstream')
            for child in lineage.get('downstream', []):
                if child['id'] not in directly_affected:
                    indirectly.append(child['id'])
        return list(set(indirectly))

    def _is_report(self, node_id: str) -> bool:
        """리포트 여부 확인"""
        node = self.lineage.lineage_graph.get(node_id)
        return node and node.get('metadata', {}).get('type') == 'report'

    def _is_dashboard(self, node_id: str) -> bool:
        """대시보드 여부 확인"""
        node = self.lineage.lineage_graph.get(node_id)
        return node and node.get('metadata', {}).get('type') == 'dashboard'

    def _assess_risk(self, affected_nodes: List[str],
                    change_type: str) -> str:
        """위험도 평가"""
        risk_score = 0

        # 영향받는 노드 수
        risk_score += min(len(affected_nodes) * 10, 50)

        # 변경 유형
        if change_type == 'SCHEMA_CHANGE':
            risk_score += 30
        elif change_type == 'DATA_DELETION':
            risk_score += 40
        elif change_type == 'VALUE_CHANGE':
            risk_score += 20

        # 리포트/대시보드 영향
        reports = [n for n in affected_nodes if self._is_report(n)]
        dashboards = [n for n in affected_nodes if self._is_dashboard(n)]

        if reports or dashboards:
            risk_score += 20

        # 위험도 레벨 결정
        if risk_score >= 70:
            return 'CRITICAL'
        elif risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_recommendations(self, impacts: Dict,
                                 change_type: str) -> List[Dict]:
        """권장사항 생성"""
        recommendations = []

        if impacts['risk_level'] in ['HIGH', 'CRITICAL']:
            recommendations.append({
                'action': 'CONDUCT_TESTING',
                'description': f'테스트 대상: {impacts["affected_reports"]}'
            })

            recommendations.append({
                'action': 'NOTIFY_STAKEHOLDERS',
                'description': '영향받는 리포트 소유자에 알림'
            })

        if change_type == 'SCHEMA_CHANGE':
            recommendations.append({
                'action': 'UPDATE_DOCUMENTATION',
                'description': '스키마 문서 업데이트'
            })

        recommendations.append({
            'action': 'SCHEDULE_VALIDATION',
            'description': 'ETL 파이프라인 검증'
        })

        return recommendations

    def create_impact_report(self, changed_node_id: str) -> str:
        """영향도 리포트 생성"""
        impacts = self.analyze_impact(changed_node_id)

        report = f"""
        ========== IMPACT ANALYSIS REPORT ==========

        Changed Node: {impacts['changed_node']}
        Risk Level: {impacts['risk_level']}

        Affected Nodes: {len(impacts['affected_nodes'])}
        {chr(10).join([f"  - {n}" for n in impacts['affected_nodes'][:10]])}

        Affected Reports: {len(impacts['affected_reports'])}
        Affected Dashboards: {len(impacts['affected_dashboards'])}

        Recommendations:
        {chr(10).join([f"  - {r['action']}: {r['description']}" for r in impacts['recommendations']])}

        ==========================================
        """

        return report
```

## 5. 자동 리니지 문서화

### 5.1 리니지 문서 생성
```python
class LineageDocumentation:
    def __init__(self, lineage_tracker, impact_analyzer):
        self.lineage = lineage_tracker
        self.impact = impact_analyzer

    def generate_html_diagram(self, node_id: str) -> str:
        """HTML 다이어그램 생성"""
        lineage = self.lineage.get_lineage(node_id)

        # Cytoscape.js를 활용한 인터랙티브 다이어그램
        html = f"""
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.21.0/cytoscape.min.js"></script>
            <style>
                #cy {{ width: 100%; height: 100vh; }}
            </style>
        </head>
        <body>
            <div id="cy"></div>
            <script>
                var cy = cytoscape({{
                    container: document.getElementById('cy'),
                    elements: {self._convert_to_cytoscape_format(lineage)},
                    style: [
                        {{
                            selector: 'node',
                            style: {{
                                'content': 'data(id)',
                                'background-color': '#555'
                            }}
                        }},
                        {{
                            selector: 'edge',
                            style: {{
                                'line-color': '#ccc',
                                'target-arrow-color': '#ccc',
                                'target-arrow-shape': 'triangle'
                            }}
                        }}
                    ],
                    layout: {{ name: 'dagre' }}
                }});
            </script>
        </body>
        </html>
        """
        return html

    def generate_json_report(self, node_id: str) -> Dict:
        """JSON 리니지 리포트 생성"""
        lineage = self.lineage.get_lineage(node_id)
        impacts = self.impact.analyze_impact(node_id)

        return {
            'node_id': node_id,
            'lineage': lineage,
            'impact_analysis': impacts,
            'generated_at': datetime.now().isoformat()
        }

    def generate_markdown_report(self, node_id: str) -> str:
        """마크다운 리니지 리포트 생성"""
        lineage = self.lineage.get_lineage(node_id)
        impacts = self.impact.analyze_impact(node_id)

        md = f"""
# Data Lineage Report: {node_id}

## Overview
- Node Type: {lineage['node'].get('type')}
- Registered: {lineage['node'].get('metadata', {}).get('registered_at')}

## Upstream Dependencies
"""
        for upstream in lineage.get('upstream', []):
            md += f"- {upstream['id']}\n"

        md += "\n## Downstream Dependencies\n"
        for downstream in lineage.get('downstream', []):
            md += f"- {downstream['id']}\n"

        md += f"\n## Impact Analysis\n"
        md += f"- Risk Level: {impacts['risk_level']}\n"
        md += f"- Affected Nodes: {len(impacts['affected_nodes'])}\n"

        return md

    def _convert_to_cytoscape_format(self, lineage: Dict) -> str:
        """Cytoscape 형식으로 변환"""
        elements = []

        # 노드 추가
        elements.append({
            'data': {'id': lineage['node']['id']}
        })

        # 상위 노드 추가
        for upstream in lineage.get('upstream', []):
            elements.append({'data': {'id': upstream['id']}})
            elements.append({
                'data': {
                    'source': upstream['id'],
                    'target': lineage['node']['id']
                }
            })

        # 하위 노드 추가
        for downstream in lineage.get('downstream', []):
            elements.append({'data': {'id': downstream['id']}})
            elements.append({
                'data': {
                    'source': lineage['node']['id'],
                    'target': downstream['id']
                }
            })

        return json.dumps(elements)
```

## 6. 실습 프로젝트

### 6.1 프로젝트: E-Commerce 데이터 리니지 구축
```
1. 모든 데이터 소스 등록
2. ETL 변환 프로세스 매핑
3. 컬럼 레벨 리니지 추출
4. 영향도 분석 실행
5. 리니지 다이어그램 생성
6. 문서화 완성
```

## 7. 평가 기준

- [ ] 리니지 추적 시스템 구축
- [ ] Column-level 리니지 추출
- [ ] 영향도 분석 구현
- [ ] 자동 문서 생성
- [ ] 인터랙티브 다이어그램
- [ ] 프로젝트 완료

## 8. 주요 도구

| 도구 | 용도 |
|------|------|
| Apache Atlas | 메타데이터 관리 |
| OpenMetadata | 데이터 카탈로그 |
| dbt | 데이터 변환 추적 |
| Great Expectations | 품질 리니지 |
| Cytoscape.js | 리니지 시각화 |

## 9. 참고 자료

- OpenMetadata 공식 문서
- Apache Atlas 튜토리얼
- dbt Data Lineage
- "Data Governance" - 책
