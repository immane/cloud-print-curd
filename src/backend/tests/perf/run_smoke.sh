#!/usr/bin/env bash
set -euo pipefail

locust -f tests/perf/locustfile.py --headless -u 5 -r 1 -t 20s --host http://localhost:8000
