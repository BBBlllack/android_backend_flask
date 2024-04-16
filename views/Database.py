import pymysql
from flask import Blueprint, Response
from api.SqlTemplates import cursor

cursor: pymysql.Connection
db = Blueprint("db", import_name=__name__, url_prefix="/db")


@db.get("/")
@db.get("/index")
def index():
    '''
    该函数为测试函数
    :return:
    '''
    cursor.execute("select * from thread")
    row: dict
    for row in cursor.fetchall():
        # print(row.get("content"))
        return Response(row.get("content"))

