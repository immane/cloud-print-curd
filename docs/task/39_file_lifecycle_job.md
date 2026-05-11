Title: Implement file lifecycle policies & cleanup job
Part: ops

Description: Background job to delete or archive files older than retention policy; runable via cron or worker.

Inputs: retention policy env var

Outputs: worker task and management command

Acceptance criteria: Running the job marks old files deleted or moves them to archival storage.

Estimated effort: 3h

Tags: ops, backend
