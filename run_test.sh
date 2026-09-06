#!/bin/bash
set -eo pipefail

dbt run --profiles-dir .
dbt test --profiles-dir .
python3 detect_infinite_loops.py
