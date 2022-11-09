import json


def read_json_data(filepath):
    json_data = None
    with open(filepath, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return json_data


def get_duration_from_hb():
    user_duration = {}
    with open("../attachment/heartbeat.log", encoding="utf-8") as f:
        for line in f:
            heartbeat = line.strip("\n").split("|")[1]
            heartbeat = json.loads(heartbeat.replace("'", "\""))
            user = heartbeat["username"]
            if user not in user_duration:
                user_duration[user] = {"start_time": heartbeat["time"]}
            else:
                user_duration[user]["end_time"] = heartbeat["time"]
                user_duration[user]["duration_from_hb"] = int(user_duration[user]["end_time"] - user_duration[user]["start_time"])
    return user_duration


def transform2excel(dict_data):
    import pandas as pd
    import datetime
    date_format = "%Y-%m-%d %H:%M:%S"
    user_duration = get_duration_from_hb()
    for user_data in dict_data:
        for i in range(8):
            news_id = "newsID_" + str(i)
            user_data[news_id] = ""
            user_data[news_id + "_startTime"] = ""
            user_data[news_id + "_endTime"] = ""
            user_data[news_id + "_duration"] = ""
        for visit_d in user_data["visitData"]:
            visited_id = "newsID_" + str(visit_d["newsId"])
            if user_data[visited_id] != "":
                # user_data[visited_id] = 1
                # user_data[visited_id + "_startTime"] = visit_d["startTime"]
                # user_data[visited_id + "_endTime"] = visit_d["endTime"]
                # if visit_d["endTime"] is not None:
                #     s_time = datetime.datetime.strptime(visit_d["startTime"], date_format)
                #     e_time = datetime.datetime.strptime(visit_d["endTime"], date_format)
                #     user_data[visited_id + "_duration"] = (e_time - s_time).seconds
                # 有重复的访问
                visited_id = "duplicated_newsID_" + str(visit_d["newsId"])
            user_data[visited_id] = 1
            user_data[visited_id + "_startTime"] = visit_d["startTime"]
            user_data[visited_id + "_endTime"] = visit_d["endTime"]
            if visit_d["endTime"] is not None:
                s_time = datetime.datetime.strptime(visit_d["startTime"], date_format)
                e_time = datetime.datetime.strptime(visit_d["endTime"], date_format)
                user_data[visited_id + "_duration"] = (e_time - s_time).seconds
        uid = user_data["uid"]
        if user_data["duration"] is not None:
            if user_duration[uid]["duration_from_hb"] > user_data["duration"]:
                print("user:{} record duration: {} < duration from hb: {}".format(uid, user_data["duration"], user_duration[uid]["duration_from_hb"]))

    # df = pd.read_json("../attachment/statisticalData.json")
    df = pd.DataFrame.from_dict(dict_data)
    df.to_excel("../attachment/userData_v2.xlsx")
    print(df.describe())


if __name__ == '__main__':
    data = read_json_data("../attachment/statisticalData.json")
    transform2excel(data)
