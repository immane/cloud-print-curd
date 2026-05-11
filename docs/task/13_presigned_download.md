Title: Implement presigned download URL endpoint
Part: storage

Description: GET /v1/files/{id}/download returns a signed download URL for private objects.

Inputs: storage SDK, files table

Outputs: route implementation

Acceptance criteria: URL is returned and is valid for a short TTL to download the object.

Estimated effort: 2h

Tags: backend, storage
