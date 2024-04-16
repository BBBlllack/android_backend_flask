import threading
import time
import tqdm
import requests
from bs4 import BeautifulSoup
import json
import re
from SqlTemplates import insert_cate_sql, insert_thread_sql, cursor

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

def parseContent(content) -> list:
    '''
    解析文本
    :param content:
    :return:
    '''
    details = BeautifulSoup(content, "html.parser").find_all("details")
    titles_en = re.findall(re.compile(r'】.*?标题'), content)
    titles_zh = re.findall(re.compile(r'标题.*?作者'), content)
    links = BeautifulSoup(content, "html.parser").find_all("a")
    data = []
    for i in range(len(links)):
        try:
            data.append({
                "link": links[i].get("href"),
                "title_en": titles_en[i],
                "title_zh": titles_zh[i],
                "detail": details[i].getText()
            })
        except Exception as e:
            print(e)
    # for link in links:
    #     print(link, link.get("href"), len(links))
    # for title in titles_en:
    #     print(title, len(titles_en))
    # for title in titles_zh:
    #     print(title, len(titles_zh))
    # for detail in details:
    #     print(detail, len(details))
    return data


def getCategories():
    url = "https://www.arxivdaily.com/api/v3/categories?dzqSid=98876474-1709640824423&dzqPf=pc"
    # 关闭SSL验证
    resp = requests.get(url, headers=HEADERS, verify=False)
    for i in dict(resp.json()).get("Data"):
        # 处理父级分类
        cursor.execute(insert_cate_sql, (i.get("categoryId"),
                                         0 if i.get("canCreateThread") == False else 1,
                                         i.get("description"),
                                         i.get("icon"),
                                         i.get("name"),
                                         i.get("parentid"),
                                         i.get("pid"),
                                         i.get("property"),
                                         i.get("sort"),
                                         i.get("threadCount")
                                         ))
        if len(i.get("children")) > 0:
            for child in i.get("children"):
                # 处理子分类
                cursor.execute(insert_cate_sql, (child.get("categoryId"),
                                                 0 if child.get("canCreateThread") == False else 1,
                                                 child.get("description"),
                                                 child.get("icon"),
                                                 child.get("name"),
                                                 child.get("parentid"),
                                                 child.get("pid"),
                                                 child.get("property"),
                                                 child.get("sort"),
                                                 child.get("threadCount")
                                                 )
                               )
    resp.close()

def getThreadList(pid: int, page: int = 1, size: int = 10):
    if page < 1 or size < 10:
        raise Exception("page or size too small!")
    url = f"https://www.arxivdaily.com/api/v3/thread.list?perPage={size}&page={page}&filter[categoryids][0]={pid}"
    resp = requests.get(url, headers=HEADERS, verify=False)
    for k, v in dict(resp.json()).get("Data").items():
        # 数据字段
        if k == "pageData":
            thread: dict
            for thread in v:
                cursor.execute(insert_thread_sql, (
                    thread.get("threadId"),
                    thread.get("postId"),
                    thread.get("topicId"),
                    thread.get("title"),
                    thread.get("categoryId"),
                    thread.get("categoryName"),
                    thread.get("issueAt"),
                    thread.get("parentCategoryId"),
                    thread.get("parentCategoryName"),
                    thread.get("createdAt"),
                    thread.get("updatedAt"),
                    thread.get("content").get("text")
                ))
        resp.close()

def saveDB(page: int = 1, size: int = 10):
    if page < 1 or size < 10:
        raise Exception("page or size too small!")
    cursor.execute("select pid from categories")
    pids = [pid.get("pid") for pid in cursor.fetchall()]
    for pid in tqdm.tqdm(pids):
        try:
            getThreadList(pid, page, size)
        except Exception as e:
            print(e)
        time.sleep(1)

lock = threading.Lock()

def worker(cid):
    global lock
    with lock:
        getThreadList(cid)
    print(f"Finished processing categoryId: {cid}")

if __name__ == '__main__':
    # getCategories()
    # getThreadList(19)
    getThreadList(24)
    # saveDB()
    # cursor.execute("select content from thread limit 1 offset 100")
    # for row in cursor.fetchall():
    #     print(parseContent(row.get("content")))
    # pass

