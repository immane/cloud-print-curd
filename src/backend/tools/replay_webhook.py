from __future__ import annotations

import argparse
import json

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay webhook payload to backend")
    parser.add_argument("--url", default="http://localhost:8000/v1/payments/webhook/test")
    parser.add_argument("--payload", required=True, help="Path to JSON payload file")
    args = parser.parse_args()

    with open(args.payload, "r", encoding="utf-8") as f:
        payload = json.load(f)

    response = requests.post(args.url, json=payload, timeout=20)
    print(f"status={response.status_code}")
    print(response.text)


if __name__ == "__main__":
    main()
