from datetime import datetime
from time import sleep

import requests
from cryptography.fernet import Fernet
from fastapi import UploadFile
from pb_video_templater import db_tools, do_app

MAX_TRY = 120


def run_task(zip_file: UploadFile, name: str):
    temp_token = Fernet.generate_key().decode()
    task_ident = int(datetime.utcnow().timestamp())
    db_tools.add_task(task_ident, name)
    with do_app.DOApp(
        API_PASSWORD=temp_token,
        **do_app.DO_SPACE_ENV
    ) as app:
        with requests.sessions.Session() as session:
            session.auth = ('api', temp_token)
            files = {
                'zip_data': zip_file.file,
            }
            session.post(
                f'{app.url}/api/make-video_template_1/{task_ident}',
                files=files,
            )
            is_working = True
            tryers = 0
            while is_working and tryers <= MAX_TRY:
                sleep(10)
                resp = session.get(f'{app.url}/api/is-working/{task_ident}')
                is_working = True if resp.text == 'true' else False
                tryers += 1
            if is_working:
                db_tools.rm_task(task_ident)
            else:
                db_tools.make_done(task_ident)
