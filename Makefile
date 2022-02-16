dev:
	source .env && uvicorn app:app --reload --port 8000

ngrok:
	ngrok http 8000

redis:
	redis-server
