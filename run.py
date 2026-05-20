import uvicorn

from backend.config import settings


if __name__ == "__main__":
    print("=" * 72)
    print("RivalScope - AI Competitive Intelligence")
    print("=" * 72)
    print(f"Web UI: http://localhost:{settings.api_port}")
    print(f"Swagger: http://localhost:{settings.api_port}/docs")
    print(f"Text model: {settings.openai_model}")
    print(f"Vision/report model: {settings.openai_vision_model}")
    print("=" * 72)

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
