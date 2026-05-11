Title: Worker scaffold and thumbnail task (Dramatiq)
Part: worker

Description: Add Dramatiq worker configuration and a task that generates a thumbnail for image files and updates file record.

Inputs: Redis dev container, storage access

Outputs: worker process code src/app/worker.py, dramatiq tasks, modified files table to hold preview_url

Acceptance criteria: Enqueueing the task updates file.preview_url after task completes.

Estimated effort: 4h

Tags: backend, worker
