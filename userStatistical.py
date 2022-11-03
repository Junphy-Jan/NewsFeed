import enum
import time
from enum import Enum


time_format = "%Y-%m-%d %H:%M:%S"


class UserData:
    def __init__(self, user_id, start_time, channel, news_seq):
        self.user_id = user_id
        self.start_time = start_time
        self.channel = channel
        self.news_seq = news_seq
        self.end_time = None
        self.visit_data = []
        self.switch_tab = False

    def update_end_time(self, end_time):
        self.end_time = end_time

    def update_click_data(self, original_news_id):
        self.visit_data.append((original_news_id, time.time()))

    def update_switch_tab(self):
        self.switch_tab = True

    def get_info(self):
        return {"uid": self.user_id, "startTime": time.strftime(time_format, time.localtime(self.start_time)),
                "channel": self.channel, "newsSeq": self.news_seq,
                "endTime": time.strftime(time_format, time.localtime(self.end_time)) if self.end_time is not None else None,
                "visitData": [{"newsId": news_id, "time": time.strftime(time_format, time.localtime(visit_time))} for news_id, visit_time in self.visit_data],
                "switch_tab": self.switch_tab}


class Channel(Enum):
    paper_news = enum.auto()
    web_news = enum.auto()


if __name__ == '__main__':
    print(Channel.paper_news.value)
    print(Channel.web_news.value)
