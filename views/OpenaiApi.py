from pymysql.cursors import DictCursor
from flask import Blueprint, request, Response, jsonify, make_response
from openai import OpenAI
from api.SqlTemplates import *
import json
import logging as log

cursor: DictCursor

key = ""

client = OpenAI(api_key=key)
OpenApi = Blueprint(name="openai", import_name=__name__, url_prefix="/openai")


def analy(info: str = "", max_tokens: int = None):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant who is good at summarizing"},
            {"role": "user", "content": "help me Summarize from the following information use chinese\n" + info}
        ],
        max_tokens=max_tokens
    )
    return completion.choices[0].message


def analyKeyword(info: str = "", max_tokens: int = None, keynum=5):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are good at extracting keywords from text"},
            {"role": "user",
             "content": f"help me extract {keynum} keywords from the following information use chinese\n" + info}
        ],
        max_tokens=max_tokens
    )
    return completion.choices[0].message


@OpenApi.get("/index")
def index():
    return "openai..."


@OpenApi.get("/analy")
def analySever():
    args = request.args
    ids: list = tuple(eval(args.get("ids")))
    print(ids, type(ids), len(ids))
    if len(ids) == 1:
        sql = f"select * from paper where id = {ids[0]}"
    else:
        sql = f"select * from paper where id in {ids}"
    cursor.execute(sql)
    results = []
    for row in cursor.fetchall():
        title_en = row.get("title_en")
        detail_en = row.get("detail_en")
        results.append(analy(f"{title_en}\n{detail_en}").__dict__)
    print(results)
    # 创建响应对象并设置 Content-Type
    response = make_response(jsonify(results))
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response


@OpenApi.get("/analykeyword")
def analySever1():
    args = request.args
    ids: list = tuple(eval(args.get("ids")))
    print(ids, type(ids))
    sql = f"select * from paper where id in {ids}"
    cursor.execute(sql)
    results = []
    for row in cursor.fetchall():
        title_en = row.get("title_en", "")
        detail_en = row.get("detail_en", "")
        results.append(analyKeyword(f"{title_en}\n{detail_en}"))
    print(results)
    return str(results)


@OpenApi.get("/summarize")
def summarize():
    global cursor
    args = request.args
    id = args.get("id", None)
    if not id:
        return Response("id is null", status=400)
    sql = f"select * from paper where id = {id}"
    cursor.execute(sql)
    summary = ""
    keywords = ""
    for row in cursor.fetchall():
        row: dict
        title_en = row.get("title_en", "")
        detail_en = row.get("detail_en", "")
        summary = analy(f"{title_en}\n{detail_en}").__dict__
        keywords = analyKeyword(f"{title_en}\n{detail_en}").__dict__
    res = {}
    res["summary"] = summary
    res["keywords"] = keywords
    print(f"res: {res}")
    return res
