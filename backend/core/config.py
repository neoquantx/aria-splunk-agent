from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	SPLUNK_HOST: str = "localhost"
	SPLUNK_PORT: int = 8089
	SPLUNK_USERNAME: str = "admin"
	SPLUNK_PASSWORD: str
	SPLUNK_WEB_PORT: int = 8000
	SPLUNK_MCP_TOKEN: str = ""
	SPLUNK_MCP_URL: str = "http://localhost:8765"
	SPLUNK_AI_ASSISTANT_URL: str = ""
	DEBUG: bool = False
	LOG_LEVEL: str = "INFO"
	CORS_ORIGIN: str = "http://localhost:5173"

	@property
	def splunk_base_url(self) -> str:
		return f"https://{self.SPLUNK_HOST}:{self.SPLUNK_PORT}"


settings = Settings()
