# coding=utf-8
import tqdm
from SqlTemplates import cursor
from openai import OpenAI
from pathlib import Path
from bs4 import BeautifulSoup
import re
from pydub import AudioSegment
from pydub.playback import play

key = ""
client = OpenAI(api_key=key)


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
    for i in range(min(len(details), len(titles_zh), len(titles_en), len(links))):
        try:
            data.append({
                "link": links[i].get("href"),
                "title_en": titles_en[i].strip("】").rstrip("<br><b>标题"),
                "title_zh": titles_zh[i].strip("标题</b>：").rstrip("<br><small><b>作者"),
                "detail_zh": re.findall(re.compile("摘要.*?摘要"), details[i].getText())[0].rstrip("摘要"),
                "detail_en": details[i].getText().rsplit("摘要", maxsplit=1)[1]
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


def genImage():
    response = client.images.generate(
        model="dall-e-3",
        prompt="a white siamese cat",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response


def text2Speech():
    speech_file_path = Path(__file__).parent / "files" / "speech.mp3"
    print(speech_file_path)
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input="涂耀锴是一个大笨比"
    )
    response.stream_to_file(speech_file_path)


def playsound(file):
    song = AudioSegment.from_file(file, file.rsplit(".", maxsplit=1)[1])
    play(song)

def vision():
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://ei.phncdn.com/videos/202109/07/394306211/original/(m=eaSaaTbaAaaaa)(mh=eMrpennKkg---2P5)12.jpg",
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    print(response)

def analy(info: str = "", max_tokens: int = None):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant who is good at summarizing"},
            {"role": "user", "content": "help me Summarize from the following information \n" + info}
        ],
        max_tokens=max_tokens
    )
    return completion.choices[0].message


if __name__ == '__main__':
    # genImage()
    # text2Speech()
    # playsound("/Users/shj/PycharmProjects/pythonProject/PythonStudy/flaskpro/AndroidServer/api/files/speech.mp3")
    # cursor.execute("select * from paper limit 1")
    # for row in cursor.fetchall():
    #     row: dict
    #     text = row.get("title_en") + ". " + row.get("detail_en")
    #     print(analy(text, 50))
    #     break
    text = '''
    请帮我两句话总结
    在机器学习和深度学习的动态领域，模型的鲁棒性和可靠性至关重要，尤其是在关键的现实应用中。这一领域的一个根本挑战是管理分布外（OOD）样本，这大大增加了模型错误分类和不确定性的风险。我们的工作通过增强神经网络中OOD样本的检测和管理来应对这一挑战。我们介绍了OOD-R（Out-of-Distribution-Rectified），这是一个精心策划的开源数据集集合，具有增强的降噪特性。现有OOD数据集中的分布（ID）噪声可能导致检测算法的评估不准确。认识到这一点，OOD-R结合了噪声过滤技术来细化数据集，确保对OOD检测算法进行更准确和可靠的评估。这种方法不仅提高了数据的整体质量，而且有助于更好地区分OOD和ID样本，从而使模型准确性提高2.5%，误报率降低至少3.2%。此外，我们提出了ActFun，这是一种创新的方法，可以微调模型对不同输入的响应，从而提高特征提取的稳定性并最大限度地减少特异性问题。ActFun解决了OOD检测中模型过度自信的常见问题，通过策略性地减少隐藏单元的影响，增强了模型更准确地估计OOD不确定性的能力。在OOD-R数据集中实现ActFun导致了显着的性能增强，包括GradNorm方法的AUROC增加18.42%，能量方法的FPR 95减少16.93%。总的来说，我们的研究不仅推进了OOD检测的方法，而且强调了数据集完整性对准确算法评估的重要性。
    '''
    print(analy(text,max_tokens=50))
