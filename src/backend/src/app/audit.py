from __future__ import annotations

from fastapi import FastAPI, Request
from sqlalchemy import insert

from src.app.db import async_session_factory
from src.app.models import AdminAuditLog
from src.app.services.auth import decode_token


def install_admin_audit_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def admin_audit_middleware(request: Request, call_next):
        response = await call_next(request)

        if not request.url.path.startswith("/admin/"):
            return response
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return response

        auth_header = request.headers.get("authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
        admin_user_id = None
        if token:
            try:
                payload = decode_token(token)
                admin_user_id = int(payload.get("sub")) if payload.get("sub") else None
            except Exception:
                admin_user_id = None

        # Insert using the underlying table and column names to avoid
        # interacting with ORM-level @property attributes (e.g. `before`/`after`)
        # which are defined as Python properties on the model and not
        # column descriptors. Passing those to insert(ORMModel) causes
        # SQLAlchemy to attempt ORM bulk persistence logic and fail with
        # "'property' object has no attribute '_bulk_update_tuples'".
        async with async_session_factory() as db:
            await db.execute(
                insert(AdminAuditLog.__table__).values(
                    admin_user_id=admin_user_id,
                    action=f"{request.method} {request.url.path}",
                    target_type="api",
                    target_id=request.url.path,
                    before=None,
                    after={"status": response.status_code},
                    ip_address=request.client.host if request.client else None,
                )
            )
            await db.commit()

        return response
