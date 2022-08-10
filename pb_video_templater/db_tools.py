from pb_video_templater import db, models, schemas, do_app
from datetime import datetime
from boto3 import session as s3_session


def add_task(ident: int, name: str):
    with db.SessionLocal() as session:
        session.add(models.Video(id=ident, name=name))
        session.commit()


def rm_task(ident: int):
    with db.SessionLocal() as session:
        task = session.query(models.Video).filter_by(id=ident).first()
        session.delete(task)
        session.commit()


def make_done(ident: int):
    with db.SessionLocal() as session:
        task = session.query(models.Video).filter_by(id=ident).first()
        task.in_working = False
        task.file_key = f'{ident}.mp4'
        session.commit()


def get_local_items_data() -> schemas.Page:
    page = schemas.Page()
    with db.SessionLocal() as session:
        videos = session.query(models.Video).all()
        for video in videos:
            page.items.append(schemas.Item(
                uid=video.id,
                name=video.name,
                date=datetime.fromtimestamp(video.id),
                in_working=video.in_working,
            ))
    return page


def rm_video(ident: int):
    with db.SessionLocal() as session:
        video = session.query(models.Video).filter_by(id=ident).first()
        do_session = s3_session.Session()
        client = do_session.client(
            's3',
            region_name=do_app.DO_SPACE_REGION,
            endpoint_url=do_app.DO_SPACE_ENDPOINT,
            aws_access_key_id=do_app.DO_SPACE_KEY,
            aws_secret_access_key=do_app.DO_SPACE_SECRET
        )
        client.delete_object(Bucket=do_app.DO_SPACE_BUCKET, Key=video.file_key)
        client.close()
        session.delete(video)
        session.commit()


def get_link(ident: int) -> str:
    with db.SessionLocal() as session:
        video = session.query(models.Video).filter_by(id=ident).first()
        do_session = s3_session.Session()
        client = do_session.client(
            's3',
            region_name=do_app.DO_SPACE_REGION,
            endpoint_url=do_app.DO_SPACE_ENDPOINT,
            aws_access_key_id=do_app.DO_SPACE_KEY,
            aws_secret_access_key=do_app.DO_SPACE_SECRET
        )
        link = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': do_app.DO_SPACE_BUCKET,
                'Key': video.file_key,
            },
            ExpiresIn=300
        )
        client.close()
    return link


def check_correct_local_data():
    with db.SessionLocal() as session:
        do_session = s3_session.Session()
        client = do_session.client(
            's3',
            region_name=do_app.DO_SPACE_REGION,
            endpoint_url=do_app.DO_SPACE_ENDPOINT,
            aws_access_key_id=do_app.DO_SPACE_KEY,
            aws_secret_access_key=do_app.DO_SPACE_SECRET
        )
        bucket_objects = client.list_objects(Bucket=do_app.DO_SPACE_BUCKET)
        bucket_object_keys = []
        for bucket_object in bucket_objects.get('Contents', []):
            bucket_object_keys.append(bucket_object['Key'])
            video = session.query(models.Video).filter_by(file_key=bucket_object['Key']).first()
            if video:
                continue
            client.delete_object(Bucket=do_app.DO_SPACE_BUCKET, Key=bucket_object['Key'])
        videos = session.query(models.Video).all()
        for video in videos:
            in_working_more_hour = datetime.utcnow().timestamp() - video.id > 3600
            is_exist_in_space = video.file_key in bucket_object_keys or video.in_working
            if video.in_working and in_working_more_hour and not is_exist_in_space:
                session.delete(video)
            elif video.in_working and in_working_more_hour and is_exist_in_space:
                video.in_working = False
            elif not video.in_working and video.file_key not in bucket_object_keys:
                session.delete(video)
        session.commit()
        amount_in_working_videos = session.query(models.Video).filter_by(in_working=True).count()
        if amount_in_working_videos == 0:
            do_app.flush_all_apps()
        client.close()
