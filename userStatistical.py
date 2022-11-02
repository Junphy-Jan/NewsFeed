import time


class UserData:
    def __init__(self, user_id, start_time, channel, news_seq):
        self.user_id = user_id
        self.start_time = start_time
        self.channel = channel
        self.news_seq = news_seq
        self.end_time = None
        self.visit_data = []

    def update_end_time(self, end_time):
        self.end_time = end_time

    def update_click_data(self, original_news_id):
        self.visit_data.append((original_news_id, time.time()))

