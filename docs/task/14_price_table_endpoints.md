Title: Implement price table read endpoints
Part: pricing

Description: GET /v1/prices and GET /v1/prices/tip returning price rules and tip text.

Inputs: a draft JSON price table (can be a static file initially)

Outputs: routes and simple storage (e.g., JSON file or DB table)

Acceptance criteria: Endpoint returns price list and tip text; client can filter by paper_type and size.

Estimated effort: 2h

Tags: backend, prices
