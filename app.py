import json
import os
import random

from flask import Flask, render_template
from markupsafe import escape

from newsFeedUtils.loggerHelper import logger

app = Flask(__name__)


# 存放每个用户对应的随机新闻顺序
user_news_idx = {}


def load_news():
    print(os.getcwd())
    paper_news_relative_path = "static/news/paper_version"
    web_news_relative_path = "static/news/web_version"
    paper_news_list = []
    web_news_list = []

    paper_news_files = os.listdir(paper_news_relative_path)
    paper_news_files.sort()
    web_news_files = os.listdir(web_news_relative_path)
    web_news_files.sort()
    for paper_file_name, web_file_name in zip(paper_news_files, web_news_files):
        with open(os.path.join(paper_news_relative_path, paper_file_name), "r", encoding="utf-8") as f:
            news = json.load(f)
            news["lines"] = news["content"].split("\n")
            news["show_content_len"] = random.randint(50, 200)
            news["show_abstract_len"] = random.randint(50, 200)
            paper_news_list.append(news)
        with open(os.path.join(web_news_relative_path, web_file_name), "r", encoding="utf-8") as f:
            news = json.load(f)
            news["lines"] = news["content"].split("\n")
            news["show_content_len"] = random.randint(50, 200)
            news["show_abstract_len"] = random.randint(50, 200)
            web_news_list.append(news)
    return paper_news_list, web_news_list


all_paper_news_list, all_web_news_list = load_news()
print(len(all_paper_news_list))


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
    global user_news_idx
    # if uid in user_news_idx:
    #     shuffle_idx = user_news_idx[uid]
    # else:
    #     shuffle_idx = [i for i in range(len(all_paper_news_list))]
    #     random.shuffle(shuffle_idx)
    #     user_news_idx[uid] = shuffle_idx

    shuffle_idx = [i for i in range(len(all_paper_news_list))]
    random.shuffle(shuffle_idx)
    if shuffle_idx[-1] == 2:
        tmp = shuffle_idx[2]
        shuffle_idx[2] = 2
        shuffle_idx[-1] = tmp
    if shuffle_idx[-2] == 2:
        tmp = shuffle_idx[2]
        shuffle_idx[2] = 2
        shuffle_idx[-2] = tmp
    user_news_idx[uid] = shuffle_idx
    logger.info("user: {} visits newspaper version with news sequence: {}".format(escape(uid), shuffle_idx))
    news = [all_paper_news_list[i] for i in shuffle_idx]
    # all_news_list = shuffle_news(all_news_list)
    return render_template('newspaper-ov-v2.html', news_list=news, uid=uid)


@app.route('/newspaper/newspaper_read/<news_idx>/<uid>')
def read_news(news_idx, uid):
    news_idx = int(news_idx)
    # news_idx = user_news_idx[uid][news_idx]
    news_list = [all_paper_news_list[i] for i in user_news_idx[uid]]
    return render_template('newspaper_read-v2.html', news_idx=news_idx, news_list=news_list)


@app.route('/web_news/<uid>')
def web_news(uid):
    # global all_news_list
    global user_news_idx
    if uid in user_news_idx:
        shuffle_idx = user_news_idx[uid]
    else:
        shuffle_idx = [i for i in range(len(all_paper_news_list))]
        random.shuffle(shuffle_idx)
        user_news_idx[uid] = shuffle_idx
    logger.info("user: {} visits web version with news sequence: {}".format(escape(uid), shuffle_idx))
    news = [all_web_news_list[i] for i in shuffle_idx]
    return render_template('web-format-overview.html', news_list=news, uid=uid)


@app.route('/web_news/web_news_read/<news_idx>/<uid>')
def read_web_news(news_idx, uid):
    news_idx = int(news_idx)
    news_list = [all_paper_news_list[i] for i in user_news_idx[uid]]
    return render_template('web-format-read.html', news=news_list[news_idx])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
