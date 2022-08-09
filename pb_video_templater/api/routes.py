from fastapi import APIRouter
from pb_video_templater.api.local_routes import api

routes = APIRouter()

routes.include_router(api.router, prefix='/api')
