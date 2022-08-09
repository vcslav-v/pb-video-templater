from fastapi import FastAPI
from pb_video_templater.api.routes import routes

app = FastAPI(debug=True)

app.include_router(routes)
