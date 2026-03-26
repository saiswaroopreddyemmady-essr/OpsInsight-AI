"""
Airflow DAG showing a production-style recurring workflow.

The local demo runs through `python -m src.pipeline`; this DAG demonstrates
how the same work can be decomposed into scheduled operational tasks.
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="ops_insight_daily",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["analytics", "data-quality", "agentic"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command="python -m src.generate_data",
    )

    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command="python -m src.pipeline",
    )

    generate_data >> run_pipeline
