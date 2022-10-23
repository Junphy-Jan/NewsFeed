import json
import os
import random

from flask import Flask, render_template
from markupsafe import escape

from newsFeedUtils.loggerHelper import logger

app = Flask(__name__)


def load_news():
    print(os.getcwd())
    news_relative_path = "static/news/"
    news_list = []
    news_files = os.listdir(news_relative_path)
    news_files.sort()
    for file_name in news_files:
        with open(os.path.join(news_relative_path, file_name), "r", encoding="utf-8") as f:
            news = json.load(f)
            news["lines"] = news["content"].split("\n")
            news["show_content_len"] = random.randint(50, 200)
            news["show_abstract_len"] = random.randint(50, 200)
            news_list.append(news)
    return news_list


all_news_list = load_news()
print(len(all_news_list))


def shuffle_news(news_list):
    # 第3、4、5位的新闻确保是news3,news4,news5
    part1 = news_list[:2] + news_list[5:]
    part2 = news_list[2:5]
    random.shuffle(part1)
    random.shuffle(part2)
    return part1[:2] + part2 + part1[2:]


# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'
@app.route('/newspaper/<uid>')
def newspaper(uid):
    # global all_news_list
    logger.info("user: {}".format(escape(uid)))
    random.shuffle(all_news_list)
    # all_news_list = shuffle_news(all_news_list)
    return render_template('newspaper.html', news_list=all_news_list)


@app.route('/newspaper/newspaper_read/<news_idx>')
def read_news(news_idx):
    news_idx = int(news_idx)
    return render_template('newspaper_read.html', news_idx=news_idx, news_list=all_news_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
