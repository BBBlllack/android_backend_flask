from bs4 import BeautifulSoup
from SqlTemplates import cursor
import re
import tqdm


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
            details_one = details[i].getText().split("摘要")
            data.append({
                "link": links[i].get("href"),
                "title_en": titles_en[i].strip("】").strip("<br><b>标题"),
                "title_zh": titles_zh[i].strip("标题</b>：").strip("<br><small><b>作者"),
                "detail_en": details_one[2].strip("："),
                "detail_zh": details_one[1].strip("："),
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


if __name__ == '__main__':
    sql = "select * from thread order by updatedAt desc"
    all = cursor.execute(sql)
    row: dict
    fail = 0
    exs = set()
    for row in tqdm.tqdm(cursor.fetchall()):
        try:
            sql_ip = "insert into paper(id, postid, title_zh, title_en, author, link, comment, detail_en, detail_zh,pid, createdAt) " \
                     "values(null,%s,%s,%s,null,%s,null,%s,%s,%s,%s)"
            postid = row.get("postId")
            content = row.get("content")
            pc = parseContent(content)
            pid = row.get("categoryId")
            ctime = str(row.get("updatedAt"))
            r: dict
            print(postid)
            for r in pc:
                cursor.execute(sql_ip,
                               (postid, r.get("title_zh", None), r.get("title_en", None),
                                r.get("link", None), r.get("detail_en", None), r.get("detail_zh", None), pid, ctime))
        except Exception as e:
            exs.add(e)
            fail += 1
    print(f"成功率:{1 - fail / all}, 异常原因有: {exs}")
