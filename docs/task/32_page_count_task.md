Title: Implement background task to compute page_count for uploaded PDFs
Part: worker

Description: Worker task that downloads file from storage, inspects PDF to count pages, updates files.page_count.

Inputs: storage access, PDF parser library (pypdf or pdfminer)

Outputs: Dramatiq task and test case

Acceptance criteria: Upload a sample PDF, run task, page_count is populated in DB.

Estimated effort: 6h

Tags: backend, worker
