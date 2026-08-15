# OpsInsight AI
### Operational Analytics, Data Quality & Decision Support Platform

OpsInsight AI is an operational analytics platform designed to combine data engineering, data quality, anomaly detection, automation, visualization, and decision support in an end-to-end workflow.

## Business Problem

Operations teams receive recurring transaction and order data from multiple systems. The incoming data may contain duplicates, missing values, pricing errors, processing delays, and unusual business patterns.

OpsInsight AI provides an automated workflow to:

- Validate incoming operational data
- Transform and model data for analytics
- Detect data-quality issues
- Identify unusual operational behavior
- Calculate business KPIs
- Prioritize analytical findings
- Generate actionable recommendations
- Present results through an interactive dashboard

## Technical Capabilities

| Capability | Implementation |
|---|---|
| Python | ETL, validation, analytics, anomaly detection, and orchestration |
| SQL | Analytical modeling, KPI queries, views, and indexing |
| Data Modeling | Fact and dimension-based analytical model |
| Data Quality | Rule-based validation framework |
| Anomaly Detection | Statistical detection of revenue and processing anomalies |
| Automation | Automated pipeline and Airflow orchestration |
| Scalable Processing | PySpark transformation workflow |
| Testing | Pytest automated tests |
| Visualization | Interactive Streamlit dashboard |
| Decision Support | Agent-based prioritization and recommendations |

## Architecture

```mermaid
flowchart LR
    A[Raw Operational Data] --> B[Python ETL]
    B --> C[(Analytical Database)]
    C --> D[Data Quality Analysis]
    C --> E[Anomaly Detection]
    C --> F[KPI Analytics]
    D --> G[Decision Orchestrator]
    E --> G
    F --> G
    G --> H[Recommendation Engine]
    H --> I[Executive Summary]
    C --> J[Streamlit Dashboard]
