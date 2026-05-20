import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routes.agents import router as agents_router
from api.v1.routes.chat import router as chat_router
from api.v1.routes.demo import router as demo_router
from api.v1.routes.incidents import router as incidents_router
from api.v1.routes.splunk import router as splunk_router
from core.config import settings
from core.splunk_client import default_splunk_client


logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


app = FastAPI(
	title="ARIA - Agentic Response & Investigation Assistant",
	version="1.0.0",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[settings.CORS_ORIGIN],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(incidents_router, prefix="/api/v1/incidents")
app.include_router(agents_router, prefix="/api/v1/agents")
app.include_router(splunk_router, prefix="/api/v1/splunk")
app.include_router(chat_router, prefix="/api/v1/chat")
app.include_router(demo_router, prefix="/api/v1/demo")


@app.get("/")
async def health_check() -> dict[str, str]:
	return {"status": "ok", "service": "ARIA", "version": "1.0.0"}


@app.on_event("startup")
async def startup_event() -> None:
	import asyncio
	is_connected = await asyncio.to_thread(default_splunk_client.test_connection)
	if is_connected:
		logger.info("Splunk connection test succeeded")
	else:
		logger.warning("Splunk connection test failed")


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
