# Generated as part of Quick Start project template 
import json
import os

from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

from cdev.resources.simple.api import Api
from cdev.resources.simple.xlambda import simple_function_annotation
from cdev.resources.simple.relational_db import RelationalDB, db_engine
from cdev import Project as cdev_project

from .models import User, Post
from .utils import Response

myProject = cdev_project.instance()

## Routes
DemoApi = Api("demoapi")

hello_route = DemoApi.route("/hello_world", "GET")

create_post_route = DemoApi.route("/post/create", "POST")

get_posts_route = DemoApi.route("/posts/get", "GET")

## DB
myDB = RelationalDB(
  "demo_db",
  db_engine.aurora_postgresql,
  "username",
  "password",
  "default_diary"
)

## Functions

cluster_arn = os.environ.get("CLUSTER_ARN")
secret_arn = os.environ.get("SECRET_ARN")
database_name = os.environ.get("DB_NAME")

engine = create_engine(f'postgresql+auroradataapi://:@/{database_name}',
                    connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))


@simple_function_annotation("hello_world_function", events=[hello_route.event()], 
environment={"CLUSTER_ARN": myDB.output.cluster_arn, "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name}, 
permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
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

@simple_function_annotation("create_post_function", events=[create_post_route.event()], 
environment={"CLUSTER_ARN": myDB.output.cluster_arn, "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name}, 
permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
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

def posts_serializer(obj_list):
    data = []
    for object in obj_list:
        dictionary = {
            'id':object.id,
            'title':object.title,
            'content':object.content
        }
        data.append(dictionary)
    print("data complete")
    return data

@simple_function_annotation("get_posts_function", events=[get_posts_route.event()], 
environment={"CLUSTER_ARN": myDB.output.cluster_arn, "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name}, 
permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
def get_posts(event, context):
    print('Hello from inside your get posts Function!')

    session = Session(engine)
    try:
        posts: Post = session.query(Post).order_by('id').all()
        data = posts_serializer(posts)
        return Response(200, body=json.dumps(data))
    except Exception as e:
        return Response(400, body=json.dumps({"message": str(e)}))




## Output
myProject.display_output("Base API URL", DemoApi.output.endpoint)
myProject.display_output("Routes", DemoApi.output.endpoints)