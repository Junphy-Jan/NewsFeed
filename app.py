import json
import os
import random
import time

from flask import Flask, render_template, request
from markupsafe import escape
from flask_socketio import SocketIO
from newsFeedUtils.loggerHelper import logger, hb_logger
from userStatistical import UserData, Channel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# 存放每个用户对应的随机新闻顺序
user_news_idx = {}
user_statistical_data = {}


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
    # logger.info("request: {}".format(request.data))
    # logger.info("request.head: {}".format(dict(request.headers)))
    global user_news_idx
    # 同一用户刷新时不会重新随机新闻顺序
    if uid in user_news_idx:
        shuffle_idx = user_news_idx[uid]
    else:
        shuffle_idx = [i for i in range(len(all_paper_news_list))]
        random.shuffle(shuffle_idx)
        user_news_idx[uid] = shuffle_idx
        user_data = UserData(uid, time.time(), Channel.paper_news.name, shuffle_idx)
        user_statistical_data[uid] = user_data

    # shuffle_idx = [i for i in range(len(all_paper_news_list))]
    # random.shuffle(shuffle_idx)
    # if shuffle_idx[-1] == 2:
    #     tmp = shuffle_idx[2]
    #     shuffle_idx[2] = 2
    #     shuffle_idx[-1] = tmp
    # if shuffle_idx[-2] == 2:
    #     tmp = shuffle_idx[2]
    #     shuffle_idx[2] = 2
    #     shuffle_idx[-2] = tmp
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
    user_statistical_data[uid].update_click_data(user_news_idx[uid][news_idx])
    return render_template('newspaper_read-v3.html', news_idx=news_idx, news_list=news_list)


@app.route('/web_news/<uid>')
def web_news(uid):
    logger.info("request: {}".format(request.data))
    logger.info("request.head: {}".format(dict(request.headers)))
    # global all_news_list
    global user_news_idx
    if uid in user_news_idx:
        shuffle_idx = user_news_idx[uid]
    else:
        shuffle_idx = [i for i in range(len(all_paper_news_list))]
        random.shuffle(shuffle_idx)
        user_news_idx[uid] = shuffle_idx
        user_data = UserData(uid, time.time(), Channel.web_news.name, shuffle_idx)
        user_statistical_data[uid] = user_data
    logger.info("user: {} visits web version with news sequence: {}".format(escape(uid), shuffle_idx))
    news = [all_web_news_list[i] for i in shuffle_idx]
    return render_template('web-format-overview.html', news_list=news, uid=uid)


@app.route('/web_news/web_news_read/<news_idx>/<uid>')
def read_web_news(news_idx, uid):
    news_idx = int(news_idx)
    news_list = [all_paper_news_list[i] for i in user_news_idx[uid]]
    user_statistical_data[uid].update_click_data(user_news_idx[uid][news_idx])
    return render_template('web-format-read.html', news=news_list[news_idx])


@app.route('/click')
def click_data():
    data = request.args
    logger.info("点击事件|args:{}".format(data))
    for i in range(len(all_paper_news_list)):
        if all_paper_news_list[i]["title"] == data["newsTitle"]:
            user_statistical_data[data["userName"]].update_click_data(i)
    return "OK"


@app.route('/leave')
def leave_data():
    data = request.args
    logger.info("点击事件|args:{}".format(data))
    user_statistical_data[data["userName"]].update_end_time(time.time())
    return "OK"


@app.route('/switch_tab')
def switch_tab():
    data = request.args
    logger.info("切换标签页|args:{}".format(data))
    user_statistical_data[data["userName"]].update_switch_tab()
    return "OK"


@app.route('/user_data')
def get_user_data():
    cur_data = [user_statistical_data[user].get_info() for user in user_statistical_data]
    # print(cur_data)
    return json.dumps(cur_data)


@socketio.on('heartbeat')
def handle_heartbeat(json_data):
    print('received json: ' + str(json_data))
    json_data["time"] = time.time()
    hb_logger.info("-heartbeat|{}".format(json_data))


@socketio.on('connect')
def handle_connect():
    print('connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
