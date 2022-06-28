import os


from sqlalchemy import select, create_engine


from sqlalchemy.orm import Session


from .models import User, Post


cluster_arn = os.environ.get("CLUSTER_ARN")


secret_arn = os.environ.get("SECRET_ARN")


database_name = os.environ.get("DB_NAME")


engine = create_engine(f'postgresql+auroradataapi://:@/{database_name}',
                    connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))


def hello_world(event, context):
    print('Hello from inside your Function!')

    session = Session(engine)

    stmt = select(User).where(User.name == 'Paul Atreides')

    for user in session.scalars(stmt):
        print(user)

    return {
        "status_code": 200,
        "message": "Hello Outside World!"
    }
