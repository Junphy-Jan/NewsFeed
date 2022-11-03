import enum
import time
from enum import Enum

time_format = "%Y-%m-%d %H:%M:%S"


class Channel(Enum):
    paper_news = enum.auto()
    web_news = enum.auto()


class NewsVisitData:
    def __init__(self, news_id):
        self.news_id = news_id
        self.start_time = time.time()
        self.end_time = None

    def update_end_time(self):
        self.end_time = time.time()


class EndType(Enum):
    closeButton = enum.auto()
    closeTab = enum.auto()


class UserData:
    def __init__(self, user_id, start_time, channel, news_seq):
        self.user_id = user_id
        self.start_time = start_time
        self.channel = channel
        self.news_seq = news_seq
        self.end_time = None
        self.visit_data = []
        self.switch_tab = False
        self.end_type = EndType.closeTab.name

    def update_end_time(self, end_time):
        self.end_time = end_time
        self.end_type = EndType.closeButton.name
        self.visit_data[-1].update_end_time()

    def update_click_data(self, original_news_id, channel):
        if channel == Channel.paper_news:
            nvd = NewsVisitData(original_news_id)
            # 更新上一个新闻的结束阅读时间
            if len(self.visit_data) > 0:
                self.visit_data[-1].update_end_time()
            self.visit_data.append(nvd)
        else:
            # 网页版新闻结束时间另行更新
            nvd = NewsVisitData(original_news_id)
            self.visit_data.append(nvd)

    def update_web_news_end_read(self):
        if len(self.visit_data) == 0:
            pass
        else:
            self.visit_data[-1].update_end_time()

    def update_switch_tab(self):
        self.switch_tab = True

    def get_info(self):
        read_data = [{"newsId": nvd.news_id,
                      "startTime": time.strftime(time_format, time.localtime(nvd.start_time)),
                      "endTime": time.strftime(time_format, time.localtime(nvd.end_time)) if nvd.end_time is not None else None}
                     for nvd in self.visit_data]
        return {"uid": self.user_id, "startTime": time.strftime(time_format, time.localtime(self.start_time)),
                "channel": self.channel, "newsSeq": self.news_seq,
                "endTime": time.strftime(time_format,
                                         time.localtime(self.end_time)) if self.end_time is not None else None,
                "visitData": read_data,
                "readCount": len(read_data),
                "switch_tab": self.switch_tab,
                "duration": int(self.end_time - self.start_time) if self.end_time is not None else None
                }


if __name__ == '__main__':
    print(Channel.paper_news.value)
    print(Channel.web_news.value)
