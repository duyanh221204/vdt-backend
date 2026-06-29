import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest, Histogram
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from configuration.app_init import init
from configuration.database import async_engine
from configuration.rate_limit import limiter
from exception.global_exception_handler import add_exception_handlers
from router import auth_router, student_router, user_router

REQUEST_COUNTER = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in {'/metrics', '/favicon.ico'}:
            return await call_next(request)

        route = request.scope.get('route')
        endpoint = route.path if route else request.url.path

        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            duration = time.perf_counter() - start

            REQUEST_COUNTER.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()

            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init()
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(MetricsMiddleware)

add_exception_handlers(app)


@app.get('/', tags=['Root'])
@limiter.limit('10/minute')
async def root(request: Request):
    return {'message': 'Hello Viettel Digital Talent 2026!'}


@app.get('/metrics')
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(user_router.router)
