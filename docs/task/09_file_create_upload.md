Title: Implement file upload intent endpoint (presign)
Part: storage

Description: POST /v1/files/create-upload should validate input and return presigned POST fields (S3 or MinIO) or token for Qiniu.

Inputs: S3 credentials env, uploads table design (entities.md)

Outputs: route implementation, uploads table migration

Acceptance criteria: Endpoint returns upload_url and fields; a subsequent curl multipart POST with those fields and a small file results in object stored in MinIO bucket.

Estimated effort: 4h

Tags: backend, storage, upload
