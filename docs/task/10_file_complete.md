Title: Implement file complete endpoint and file record creation
Part: storage

Description: POST /v1/files/complete that verifies uploaded object, stores checksum/metadata, and creates a files DB record.

Inputs: presigned create-upload output, storage SDK access

Outputs: route implementation, files table migration

Acceptance criteria: After upload and complete call, GET /v1/files returns the new file with status ready.

Estimated effort: 4h

Tags: backend, storage
