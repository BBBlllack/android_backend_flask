import datetime
import os
from io import BytesIO
import random

import fitz
import requests
from flask import Blueprint, request, Response
from pymysql.cursors import DictCursor
from flask import Blueprint, request, send_file, render_template
from api.SqlTemplates import *
import PyPDF2

from wordcloud import WordCloud

cursor: DictCursor

Word = Blueprint(name="word", import_name=__name__, url_prefix="/word")


def pyMuPDF_fitz(pdfPath):
    startTime_pdf2img = datetime.datetime.now()  # 开始时间

    pdfDoc = fitz.open(pdfPath)
    imagePaths = []
    for pg in range(pdfDoc.page_count):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
        pix: fitz.Pixmap = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(f"static/images/page_{pg + 1}.png")  # 将图片写入指定的文件夹内
        imagePaths.append(f"/static/images/page_{pg + 1}.png")
    endTime_pdf2img = datetime.datetime.now()  # 结束时间
    print('pdf2img时间=', (endTime_pdf2img - startTime_pdf2img).seconds)
    return imagePaths


@Word.get("/")
@Word.get("/index")
def index():
    return "word..."


@Word.get("/generate")
def generate():
    args = request.args
    id = args.get("id", None)
    width = args.get("width", 800)
    height = args.get("height", 400)
    if not id:
        return Response("id is null!", status=400)
    cursor.execute(f"select * from paper where id = {id}")
    # 获取要生成词云的文章
    data = cursor.fetchall()
    if len(data) <= 0:
        return Response("id is not exist!", status=400)
    for element in data:
        element: dict
        text = element.get("detail_en", "") + element.get("title_en", "")
        # 创建词云对象
        wordcloud = WordCloud(width=width, height=height, background_color="white",
                              max_words=100, colormap='viridis',
                              contour_color='black', contour_width=3).generate(text)
        # 将词云图像保存到内存中
        image_stream = BytesIO()
        wordcloud.to_image().save(image_stream, format='PNG')
        image_stream.seek(0)
        # 保存图像后关闭文件对象
        image_data = image_stream.getvalue()
        image_stream.close()
        # 发送词云图像文件给客户端
        return send_file(BytesIO(image_data), mimetype='image/png')


@Word.route("/preview")
def preview():
    if not request.args.get("key",None):
        return Response("接口禁用!", status=403)
    headers = request.headers
    addr = request.remote_addr
    print(headers, addr)
    # 创建一个 PyPDF2 的 PdfFileReader 对象
    pdf_file = open('/Users/shj/PycharmProjects/pythonProject/PythonStudy/pdfUtils/2402.09339v1.pdf', 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # 获取 PDF 文件的页数
    num_pages = len(pdf_reader.pages)
    # 逐页读取内容
    all = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        all += f"{text}\n"
    pdf_file.close()
    return render_template("pdf.html", content=all)
    # 关闭 PDF 文件


@Word.route("/preimg")
def preview1():
    args = request.args
    base_path = "static/pdf/"
    pdf_url = args.get("url", "http://arxiv.org/pdf/2404.06773v1")
    name = pdf_url.rsplit("/", maxsplit=1)[1]
    if name not in os.listdir(base_path):
        resp = requests.get(pdf_url)
        with open(f"{base_path}{name}", mode="wb") as file:
            file.write(resp.content)
        resp.close()
    # 定义 PDF 文件路径
    pdf_file = f"{base_path}{name}"
    paths = pyMuPDF_fitz(pdf_file)
    # 渲染模板并传递图片路径列表
    return render_template("pdfimg.html", image_paths=paths)
