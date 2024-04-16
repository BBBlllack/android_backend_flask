import random
from flask import Blueprint, request, Response
from pymysql.cursors import DictCursor
from flask import Blueprint, request, send_file
from api.SqlTemplates import *
import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging as log

cursor: DictCursor

Recommend = Blueprint(name="Recommend", import_name=__name__, url_prefix="/recom")

def getData() -> pandas.DataFrame:
    # 定义查询语句
    sql = "SELECT * FROM paper limit 10000"
    cursor.execute(sql)
    results = cursor.fetchall()

    # 将查询结果组织成需要的格式
    def convert_to_data_format(results):
        data_format = []
        for row in results:
            row: dict
            paper_data = {
                'id': row.get('id'),
                # 'postid': row.get('postid'),
                'title_zh': row.get('title_zh'),
                # 'title_en': row.get('title_en'),
                'author': row.get('author'),
                # 'link': row.get('link'),
                # 'comment': row.get('comment'),
                # 'detail_en': row.get('detail_en'),
                'detail_zh': row.get('detail_zh'),
                # 'createdAt': row.get('createdAt').isoformat() if row.get('createdAt') else None,
                # 'pid': row.get('pid'),
                # 'favor': row.get('favor'),
                # 'pname': row.get('pname'),
                # 'fid': row.get('fid'),
                # 'fname': row.get('fname')
            }
            data_format.append(paper_data)
        return data_format

    # 调用函数转换数据格式
    converted_data = convert_to_data_format(results)
    return pandas.DataFrame(converted_data)


def recommend_paper_byid(df, id, cosine_sim, top_n=5) -> pandas.DataFrame:
    cond = (id == df['id'])
    idx = df[cond].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]
    paper_indices = [i[0] for i in sim_scores]
    return df.iloc[paper_indices]


@Recommend.get("/byid")
def byid():
    args = request.args
    id = int(args.get("id", random.randint(1, 10000)))
    num = int(args.get("num", 5))
    if num < 1 or num > 50:
        return []
    # 获取全部数据
    data = getData()
    # 我们使用 TF-IDF 来提取文本特征并进行向量化
    tfidf_vectorizer = TfidfVectorizer(stop_words=['english'])
    tfidf_matrix = tfidf_vectorizer.fit_transform(data['detail_zh'])

    # 我们使用余弦相似度来计算文本之间的相似度
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 测试推荐算法
    recommended_papers = recommend_paper_byid(df=data, id=id, cosine_sim=cosine_sim, top_n=num)

    # 返回推荐的文章id列表
    return recommended_papers['id'].tolist()
