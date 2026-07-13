import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("ezio.api")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        req_id = getattr(request.state, "request_id", "unknown")
        
        logger.info(f"[{req_id}] {request.method} {request.url.path} started")
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"[{req_id}] {request.method} {request.url.path} completed in {process_time:.3f}s with status {response.status_code}")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[{req_id}] {request.method} {request.url.path} FAILED in {process_time:.3f}s - {str(e)}", exc_info=True)
            raise

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(e),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )

def setup_middlewares(app):
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, restrict to Electron localhost origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
