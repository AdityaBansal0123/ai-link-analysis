import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from app.config import settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse, ErrorResponse, ErrorDetail
from app.services.analysis_service import AnalysisService
from app.ui import HTML_UI
from app.utils.validators import (
    LinkAnalysisException,
    InvalidURLError,
    SSRFSecurityError,
    WebsiteInaccessibleError,
    WebsiteTimeoutError,
    LLMServiceError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("dxora-link-analysis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    effective_provider = settings.get_effective_provider()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Effective LLM Provider: {effective_provider}")
    yield
    logger.info("Shutting down Link Analysis API.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## AI-Powered Website Link Analysis API

An enterprise-ready FastAPI service that extracts, comprehends, and evaluates website content using Large Language Models to deliver actionable business intelligence across five core dimensions:

1. **Competitor vs Your Brand Details** (Head-to-head comparison, strengths, gaps, market positioning)
2. **Top 5 Target Search Queries** (Multi-platform discovery across Google, Facebook, Instagram, LinkedIn, and X)
3. **SEO Improvement** (Keywords, SEO Title, Meta Description, and Supporting Content roadmap)
4. **Top 5 Services** (Identified from actual content, with inferred flags clearly labeled)
5. **Target Audience Identification** (Personas, business types, customer needs, and 5 market segments)

### Security Features
- Strict **Server-Side Request Forgery (SSRF)** defenses blocking private, loopback, link-local, and cloud metadata addresses.
- Safe redirect resolution intercepting chained redirect attacks.
- Graceful handling of inaccessible or slow endpoints with standard HTTP status codes.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_service = AnalysisService()


# ==========================================
# Exception Handlers
# ==========================================

@app.exception_handler(LinkAnalysisException)
async def handle_link_analysis_exception(request: Request, exc: LinkAnalysisException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code=exc.code,
                message=exc.message
            )
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0]["msg"] if errors else "Invalid request data"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=f"Request validation failed: {first_error}",
                details=errors
            )
        ).model_dump()
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal server error occurred while processing the request."
            )
        ).model_dump()
    )


# ==========================================
# API Routes
# ==========================================

@app.get("/", tags=["General"])
async def root(request: Request):
    """Welcome endpoint providing interactive UI for browsers, or JSON metadata for API clients."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=HTML_UI)
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "redoc": "/redoc",
        "analysis_endpoint": "POST /link-analysis"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint displaying server and LLM engine readiness."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "llm_provider": settings.get_effective_provider(),
        "gemini_model": settings.GEMINI_MODEL,
        "openai_model": settings.OPENAI_MODEL
    }


@app.get(
    "/link-analysis",
    tags=["Analysis"],
    summary="Information on how to use POST /link-analysis",
    include_in_schema=False
)
async def get_link_analysis_info(request: Request):
    """Provides interactive Web UI for browser navigation, or API usage guide for JSON clients."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=HTML_UI)
    return {
        "message": "The /link-analysis endpoint requires an HTTP POST request with a JSON body.",
        "usage": {
            "method": "POST",
            "url": "http://localhost:4000/link-analysis",
            "headers": {"Content-Type": "application/json"},
            "body": {"url": "https://example.com"}
        },
        "interactive_docs": "/docs",
        "description": "Please open http://localhost:4000/docs in your browser to test this endpoint interactively using the Swagger UI."
    }


@app.post(
    "/link-analysis",
    response_model=LinkAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"],
    summary="Analyze website link and generate 5-section AI intelligence report",
    responses={
        200: {"description": "Structured link analysis successfully generated."},
        400: {"model": ErrorResponse, "description": "Invalid or malformed URL syntax."},
        403: {"model": ErrorResponse, "description": "SSRF violation (internal/private IP range blocked)."},
        502: {"model": ErrorResponse, "description": "Target website was unreachable or returned an error status."},
        504: {"model": ErrorResponse, "description": "Target website request timed out."},
    }
)
async def analyze_website_link(payload: LinkAnalysisRequest):
    """
    Submits a website URL for automated extraction and multi-dimensional LLM analysis.

    - **url**: Valid HTTP or HTTPS address to analyze.
    """
    response = await analysis_service.analyze_link(payload.url)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
