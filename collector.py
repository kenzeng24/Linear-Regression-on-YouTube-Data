"""
    @Description:   This python collects data from YouTube Videos
    @               such as views, likes, dislikes, etc
    @
    @Author:        Ken Zeng
"""

import requests
from lxml import html
from datetime import datetime
import csv


class Collector(object):
    """
    A collector that takes a list of url as an input
    and scrapes data from those urls
    """
    def __init__(self, id_list):

        self.id_list = id_list
        self.valid_ids = set([])
        self.finished = False

        # records the date the views are collected
        self.date = datetime.now()

        # each dictionary maps url to the information on each url
        self.info = {}

        # set of urls that disabled one of the above
        # but what should I do with all the disabled channels?
        self.disabled = set([])

        self.url_start = "https://www.youtube.com/watch?v="
        self.url_list = [self.url_start + id for id in id_list]

    def get_views(self, input, is_url=False):
        """
        return a dictionary mapping each url to
        all the information collected on the url
        """
        if self.finished:
            if is_url:
                video_id = input[32:]
            else:
                video_id = input
            if video_id in self.disabled:
                return 0.0
            return self.info[video_id]["views"]
        else:
            print("error: must run the web scraper first!")

    def get_non_disabled(self, with_url=False):
        """
        with_url = true returns the list of urls
        with_url = false returns the list of ids
        get a list of all YouTube videos that did not disabled views
        """
        if self.finished:
            non_disabled = set()
            for video_id in self.valid_ids:
                if video_id not in self.disabled:
                    non_disabled.add(video_id)
            if with_url:
                non_disabled = [self.url_start + video_id for video_id in non_disabled]
            return non_disabled
        else:
            print("error: must run the web scraper first!")

    def run(self):
        """
        collects views, likes, dislikes of a youtube video
        It can then save the results as a csv
        """
        print("start collection...")

        for i in range(len(self.id_list)):
            # sets a check point every time 500 websites are visited
            print(i)
            if i % 10 == 0 and i != 0:
                print("visited  " + str(i) + " urls")
            video_id = self.id_list[i]
            url = "https://www.youtube.com/watch?v=" + video_id
            # check if the url is a site on YouTube
            if len(video_id) != 11:
                pass
            try:
                # try to access the webpage as an xpath
                page = requests.get(url)
                youtube = html.fromstring(page.text)
                self.info[video_id] = {}

                try:  # try to get title
                    title = youtube.xpath("//*[(@class='watch-title')]/text()")
                    self.info[video_id]["title"] = str(title[0]).split("\n")[1][4:]
                except:
                    self.disabled.append(video_id)
                try:  # try to get date
                    title = youtube.xpath("//*[(@class='watch-time-text')]/text()")
                    # Todo: how do I convert a string date to numbers?
                    self.info[video_id]["date"] = str(title[0])
                except:
                    self.disabled.append(video_id)
                try:  # try to get views
                    view_count = youtube.xpath("//*[(@class='watch-view-count')]/text()")
                    self.info[video_id]["views"] = float(str(view_count[0]).split(" ")[0].replace(',', ''))
                except:
                    self.disabled.append(video_id)

                # Todo: get correct xpaths to likes and dislikes
                # try:  # try to get likes
                #     like_counts = youtube.xpath("//*[(@class='like-button-renderer-like-button')]/text()")
                #     self.info[url]["likes"] = float(str(like_counts[0]).split(" ")[0].replace(',', ''))
                # except:
                #     disabled.append(video_id)
                # try:  # try to get dislikes
                #     dislike_counts = youtube.xpath("//*[(@class='like-button-renderer-dislike-button')]/text()")
                #     self.info[url]["dislikes"] = float(str(dislike_counts[0]).split(" ")[0].replace(',', ''))
                # except:
                #     disabled.append(video_id)

                self.valid_ids.add(video_id)
            except:
                pass

        self.finished = True
        print("Collection finished.")

    def save(self, file_name):
        """
        save contents of self.info as a csv file
        """
        if self.finished:
            csv_file = open(file_name, 'w')
            writer = csv.writer(csv_file)
            row_titles = ["video_id", "title", "date", "views"]
            writer.writerow(row_titles)

            # generate rest of the csv
            for video_id in self.valid_ids:
                if video_id not in self.disabled:
                    value = [video_id] + [self.info[video_id][name] for name in row_titles[1:]]
                    writer.writerow(value)
            csv_file.close()
            print("File saved")
        else:
            print("error: must run the web scraper first!")


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
    id_list = ["87yupacw8Jc", "1QCK_gFGi90", "ijn65GshaPs"]
    web_scraper = Collector(id_list)
    web_scraper.run()
    print(web_scraper.get_views(id_list[0]))
    # print(web_scraper.date.isocalendar())
    # datetime.fromisoformat()
    print(web_scraper.disabled)
    print(web_scraper.valid_ids)
    web_scraper.save("test.csv")

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