import pymysql
# 连接到数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='12345678',
    database='andexam',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
cursor = conn.cursor()

insert_cate_sql = """
INSERT INTO `categories` (
    `categoryId`,
    `canCreateThread`,
    `description`,
    `icon`,
    `name`,
    `parentid`,
    `pid`,
    `property`,
    `sort`,
    `threadCount`
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
);
"""

insert_thread_sql = """
INSERT INTO `thread` (
    `threadId`,
    `postId`,
    `topicId`,
    `title`,
    `categoryId`,
    `categoryName`,
    `issueAt`,
    `parentCategoryId`,
    `parentCategoryName`,
    `createdAt`,
    `updatedAt`,
    `content`
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
);
"""


