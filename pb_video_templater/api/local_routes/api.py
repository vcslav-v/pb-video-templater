import os
import secrets

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     UploadFile, status)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pb_video_templater.api import service
from pb_video_templater import db_tools

router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME') or 'root'
password = os.environ.get('API_PASSWORD') or 'pass'


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@router.post('/make-vt-1/{name}')
def make_video_template_1(
    name:  str,
    zip_file: UploadFile,
    background_tasks: BackgroundTasks,
    _: str = Depends(get_current_username)
):
    background_tasks.add_task(service.run_task, zip_file, name)
    return 200


@router.get('/page')
def get_page(
    _: str = Depends(get_current_username)
):
    return db_tools.get_local_items_data()


@router.delete('/video/{ident}')
def rm_video(
    ident: int,
    _: str = Depends(get_current_username)
):
    db_tools.rm_video(ident)


@router.get('/link/{ident}')
def get_link(
    ident: int,
    _: str = Depends(get_current_username)
):
    return db_tools.get_link(ident)
