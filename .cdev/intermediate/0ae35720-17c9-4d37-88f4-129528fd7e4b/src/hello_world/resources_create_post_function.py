import json


import os


from sqlalchemy import select, create_engine


from sqlalchemy.orm import Session


from .models import User, Post


from .utils import Response


cluster_arn = os.environ.get("CLUSTER_ARN")


secret_arn = os.environ.get("SECRET_ARN")


database_name = os.environ.get("DB_NAME")


engine = create_engine(f'postgresql+auroradataapi://:@/{database_name}',
                    connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))


def create_post(event, context):
    print('Hello from inside your create post Function!')

    session = Session(engine)
    data = json.loads(event.get("body"))
    try:
        session.add(Post(title=data.get("title"), content=data.get("content")))
        session.commit()
        return Response(200, body=json.dumps({"message": "Created Post"}))
    except Exception as e:
        return Response(400, body=json.dumps({"message": str(e)}))
