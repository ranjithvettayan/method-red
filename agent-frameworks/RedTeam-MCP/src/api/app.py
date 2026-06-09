"""
FastAPI application factory and configuration
"""

import logging

logger = logging.getLogger(__name__)

# FastAPI imports (only imported when running API)
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


def create_app(include_ui: bool = True) -> "FastAPI":
    """Create and configure the FastAPI application
    
    Args:
        include_ui: Whether to include the web UI routes
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI dependencies not available")

    from src.config import config
    from src.api.endpoints import register_endpoints
    from src.api.websockets import register_websockets
    from src.api.crud import get_crud_router
    from src.db import get_db, init_db

    app = FastAPI(title="Red Team MCP API", version="1.0.0")

    # Initialize database
    db = init_db()
    
    # Initialize token on first run and migrate from YAML if needed
    token = db.get_or_create_token()
    if token:
        logger.info("=" * 60)
        logger.info("New API token generated (save this!):")
        logger.info(f"  {token}")
        logger.info("=" * 60)
    
    # Migrate from YAML config if database is empty
    if not db.is_initialized():
        logger.info("Database empty, importing from YAML config...")
        db.import_from_yaml_config(config)
        logger.info(f"Imported {len(db.get_agents())} agents and {len(db.get_teams())} teams")
    
    # Load custom providers from database
    from src.providers import reload_custom_providers
    reload_custom_providers()
    custom_providers = db.get_custom_providers()
    if custom_providers:
        logger.info(f"Loaded {len(custom_providers)} custom providers")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Request size limit middleware
    @app.middleware("http")
    async def limit_request_size(request: Request, call_next):
        max_size = config.get("api.max_request_size", 1024 * 1024)  # 1MB default
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request too large. Maximum size: {max_size} bytes",
                    )
            except ValueError:
                pass  # Invalid content-length, let it pass for now
        response = await call_next(request)
        return response

    # Register REST endpoints
    register_endpoints(app, limiter, config)

    # Register WebSocket endpoints
    register_websockets(app, config)
    
    # Register CRUD API endpoints
    crud_router = get_crud_router()
    if crud_router:
        app.include_router(crud_router)
    
    # Register Web UI routes
    if include_ui:
        try:
            from src.web.routes import router as ui_router
            app.include_router(ui_router, prefix="/ui", tags=["ui"])
            logger.info("Web UI available at /ui/")
        except ImportError as e:
            logger.warning(f"Web UI not available: {e}")

    return app


# Create the app instance
app = create_app() if FASTAPI_AVAILABLE else None
