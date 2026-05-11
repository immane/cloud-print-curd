from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from src.app.audit import install_admin_audit_middleware
from src.app.config import settings
from src.app.middleware import install_metrics_middleware
from src.app.routes.addresses import router as addresses_router
from src.app.routes.admin_audit import router as admin_audit_router
from src.app.routes.admin_auth import router as admin_auth_router
from src.app.routes.admin_files import router as admin_files_router
from src.app.routes.admin_library import router as admin_library_router
from src.app.routes.admin_metrics import router as admin_metrics_router
from src.app.routes.admin_orders import router as admin_orders_router
from src.app.routes.admin_prices import router as admin_prices_router
from src.app.routes.admin_search import router as admin_search_router
from src.app.routes.admin_users import router as admin_users_router
from src.app.routes.auth_user import router as auth_user_router
from src.app.routes.auth_wechat import router as auth_wechat_router
from src.app.routes.files import router as files_router
from src.app.routes.health import router as health_router
from src.app.routes.home import router as home_router
from src.app.routes.library import router as library_router
from src.app.routes.orders import router as orders_router
from src.app.routes.payments import router as payments_router
from src.app.routes.prices import router as prices_router
from src.app.routes.metrics import router as metrics_router
from src.app.routes.support import router as support_router


def create_app() -> FastAPI:
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=settings.app_env,
        )

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    install_metrics_middleware(app)
    install_admin_audit_middleware(app)

    app.include_router(health_router)
    app.include_router(auth_wechat_router)
    app.include_router(auth_user_router)
    app.include_router(addresses_router)
    app.include_router(files_router)
    app.include_router(prices_router)
    app.include_router(home_router)
    app.include_router(library_router)
    app.include_router(orders_router)
    app.include_router(payments_router)
    app.include_router(support_router)
    app.include_router(metrics_router)

    app.include_router(admin_auth_router)
    app.include_router(admin_orders_router)
    app.include_router(admin_files_router)
    app.include_router(admin_users_router)
    app.include_router(admin_prices_router)
    app.include_router(admin_library_router)
    app.include_router(admin_metrics_router)
    app.include_router(admin_audit_router)
    app.include_router(admin_search_router)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred",
                    "details": str(exc) if settings.debug else None,
                }
            },
        )

    return app


app = create_app()
