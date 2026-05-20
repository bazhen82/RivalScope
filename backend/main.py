import base64
import json
import logging
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import BASE_DIR, settings
from backend.models.schemas import (
    AnalysisContext,
    CompareCompetitorsRequest,
    HealthResponse,
    HistoryResponse,
    ParseAnalysisResponse,
    TextAnalysisRequest,
    UrlAnalysisRequest,
)
from backend.services.ai_service import ai_service
from backend.services.history_service import history_service
from backend.services.parser_service import parser_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="RivalScope",
    description="AI competitive intelligence assistant for market and competitor analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        ai_provider=ai_service.provider_name,
    )


@app.get("/competitors")
async def competitors() -> list[dict]:
    path = BASE_DIR / "data" / "competitors.json"
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/analyze_text")
async def analyze_text(request: TextAnalysisRequest):
    try:
        result = await ai_service.analyze_text(request.text, request.context)
        history_service.add(
            "text",
            f"Текст: {request.text[:80]}",
            {
                "context": request.context.model_dump(mode="json"),
                "result": result.model_dump(mode="json"),
            },
        )
        return result
    except Exception as exc:
        logger.exception("Text analysis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/analyze_image")
async def analyze_image(
    file: UploadFile = File(...),
    context_json: str = Form("{}"),
):
    try:
        content = await file.read()
        max_bytes = settings.max_image_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Image is too large. Max size is {settings.max_image_mb} MB.",
            )
        context = AnalysisContext(**json.loads(context_json))
        image_base64 = base64.b64encode(content).decode("utf-8")
        result = await ai_service.analyze_image(
            image_base64=image_base64,
            mime_type=file.content_type or "image/png",
            context=context,
        )
        history_service.add(
            "image",
            f"Изображение: {file.filename}",
            {
                "context": context.model_dump(mode="json"),
                "result": result.model_dump(mode="json"),
            },
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Image analysis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/parse_demo", response_model=ParseAnalysisResponse)
async def parse_demo(request: UrlAnalysisRequest) -> ParseAnalysisResponse:
    try:
        parsed = await parser_service.parse(
            str(request.url), use_selenium=request.use_selenium
        )
        analysis = await ai_service.analyze_parsed_page(
            parsed.url,
            parsed.title,
            parsed.h1,
            parsed.text_excerpt,
            request.context,
        )
        response = ParseAnalysisResponse(parsed=parsed, analysis=analysis)
        history_service.add(
            "site",
            f"Сайт: {parsed.url}",
            {
                "context": request.context.model_dump(mode="json"),
                "parsed": parsed.model_dump(
                    mode="json", exclude={"screenshot_base64"}
                ),
                "analysis": analysis.model_dump(mode="json"),
            },
        )
        return response
    except Exception as exc:
        logger.exception("Site parsing/analysis failed for %s", request.url)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/compare_competitors")
async def compare_competitors(request: CompareCompetitorsRequest):
    payload = "\n\n".join(
        f"{item.name}\nURL: {item.url}\nКомментарий: {item.note or ''}"
        for item in request.competitors
    )
    try:
        result = await ai_service.compare_competitors(payload, request.context)
        competitors = [
            {
                "name": item.name,
                "url": str(item.url),
                "note": item.note,
            }
            for item in request.competitors
        ]
        history_service.add(
            "compare",
            "Сравнение конкурентов",
            {
                "context": request.context.model_dump(mode="json"),
                "competitors": competitors,
                "result": result,
            },
        )
        return result
    except Exception as exc:
        logger.exception("Competitor comparison failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/analyze_pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    raise HTTPException(
        status_code=501,
        detail="PDF analysis is planned as an extension module for the homework report.",
    )


@app.get("/history", response_model=HistoryResponse)
async def history() -> HistoryResponse:
    return HistoryResponse(items=history_service.list())


@app.delete("/history")
async def clear_history() -> dict:
    history_service.clear()
    return {"status": "cleared"}
