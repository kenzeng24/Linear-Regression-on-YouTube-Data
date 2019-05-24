"""
    @Description:   This python collects data from YouTube Videos
    @               such as views, likes, dislikes, etc
    @
    @Author:        Ken Zeng
"""

import requests
from lxml import html
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from contextlib import closing
import csv
from collections import defaultdict


class Collector(object):
    """
    A collector that takes a list of url as an input
    and scrapes data from those urls
    """
    def __init__(self, url_list):

        self.url_list = url_list
        self.valid_urls = set([])

        # records the date the views are collected
        self.date = datetime.now()

        # each dictionary maps url to the information on each url
        self.info = {}

        # set of urls that disabled one of the above
        # but what should I do with all the disabled channels?
        self.disabled = set([])

    def get_views(self, url):
        """
        return a dictionary mapping each url to
        all the information collected on the url
        """
        if url in self.disabled:
            return 0.0
        return self.info[url]["views"]

    def get_non_disabled(self):
        """
        get a list of all YouTube videos that disabled views
        """
        non_disabled = set()
        for url in self.valid_urls:
            if url not in self.disabled:
                non_disabled.add(url)
        return non_disabled

    def run(self):
        """
        collects views, likes, dislikes of a youtube video
        It can then save the results as a csv
        """
        print("start collection...")

        for i in range(len(self.url_list)):
            # sets a check point every time 500 websites are visited
            print(i)
            if i % 10 == 0 and i != 0:
                print("visited  " + str(i) + " urls")
            url = self.url_list[i]
            # check if the url is a site on YouTube
            if url[:29] != "https://www.youtube.com/watch":
                pass
            try:
                # try to access the webpage as an xpath
                page = requests.get(url)
                youtube = html.fromstring(page.text)
                self.info[url] = {}

                try:  # try to get title
                    title = youtube.xpath("//*[(@class='watch-title')]/text()")
                    self.info[url]["title"] = str(title[0])
                except:
                    self.disabled.append(url)
                try:  # try to get date
                    title = youtube.xpath("//*[(@class='watch-time-text')]/text()")
                    self.info[url]["date"] = str(title[0])
                except:
                    self.disabled.append(url)
                try:  # try to get views
                    view_count = youtube.xpath("//*[(@class='watch-view-count')]/text()")
                    self.info[url]["views"] = float(str(view_count[0]).split(" ")[0].replace(',', ''))
                except:
                    self.disabled.append(url)

                # Todo: get correct xpaths to likes and dislikes
                # try:  # try to get likes
                #     like_counts = youtube.xpath("//*[(@class='like-button-renderer-like-button')]/text()")
                #     self.info[url]["likes"] = float(str(like_counts[0]).split(" ")[0].replace(',', ''))
                # except:
                #     disabled.append(url)
                # try:  # try to get dislikes
                #     dislike_counts = youtube.xpath("//*[(@class='like-button-renderer-dislike-button')]/text()")
                #     self.info[url]["dislikes"] = float(str(dislike_counts[0]).split(" ")[0].replace(',', ''))
                # except:
                #     disabled.append(url)

                self.valid_url.append(url)
            except:
                pass

        print("Collection finished.")

    def save(self, file_name):
        """
        save the file as a csv file
        """
        csv_file = open(file_name, 'w')
        writer = csv.writer(csv_file)
        row_titles = ["url", "title", "date", "views"]
        writer.writerow(row_titles)

        # generate rest of the csv
        for url in self.valid_urls:
            if url not in self.disabled:
                value = [url] + [self.info[url][name] for name in row_titles[1:]]
                writer.writerow(value)
        csv_file.close()

        print("File saved")

def stringtoint(stringdate):
    """
    split mm/dd/yyyy into year, month and day
    """
    first = stringdate.split("T")[0]
    second = first.split("-")
    year = int(second[0])
    month = int(second[1])
    day = int(second[2])
    return year, month, day


def num_days(year,month,day):
    """
    return the number of days between the date and 0 BC
    """
    # Todo: what about leap years?
    monthdays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    return year * 365 + monthdays[month-1] + day

if __name__ == "__main__":

    print("Hello World")
    url_1 = "https://www.youtube.com/watch?v=87yupacw8Jc&t=3592s"
    url_2 = "https://www.youtube.com/watch?v=1QCK_gFGi90"
    url_list = [url_1, url_2]
    web_scraper = Collector(url_list)
    web_scraper.run()
    print(web_scraper.get_views(url_1))
    print(web_scraper.get_views(url_2))
    # print(web_scraper.date.isocalendar())
    # datetime.fromisoformat()
    # web_scraper.save("results.csv")

    # old_data = csv.reader(open("USvideos.csv"))
    # num_url = 100
    #
    # url_list = ["https://www.youtube.com/watch?v=" + item[0] for item in old_data]
    # if num_url < len(url_list):
    #     url_list = url_list[:num_url]
    # web_scraper = Collector(url_list)
    # web_scraper.run()
    # vid_dict = {}
    # count = 0
    #
    # time = web_scraper.date.fromisoformat()
    #
    # for list in old_data:
    #     if count != 0 and count < num_url:
    #         new_views = web_scraper.get_views("https://www.youtube.com/watch?v=" + list[0])
    #         if new_views != 0:
    #             year, month, date = stringtoint(list[1:][4])
    #             time_passed = num_days(year, month, date) - num_days(time[0], time[1], time[2])
    #             views = float(list[1:][6])
    #             likes = float(list[1:][7])
    #             dislikes = float(list[1:][8])
    #             comment_count = float(list[1:][9])
    #             views_change = new_views - views
    #
    #             vid_dict[list[0]] = [time_passed, views, likes, dislikes, comment_count, new_views, views_change]
    #     print count
    #     count += 1
    #
    # csv_file = open('test_run.csv', 'w')
    # writer = csv.writer(csv_file)
    # writer.writerow(
    #     ["video_id", "time_passed", "views", "likes", "dislikes", "comment_count", "new_views", "views_change"])
    # for key, value in vid_dict.items():
    #     value.insert(0, key)
    #     writer.writerow(value)
    #
    # csv_file.close()