import os
import sys
import json
import requests

import praw

def DownloadImages(amount: int, folder: str = "reddit", ext: list = [".jpg",".png"]) -> None:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\" + folder
    if not os.path.exists(__location__):
        os.makedirs(__location__)

    path = __location__
    print(path)
    url = "https://www.reddit.com/"

    with open(os.path.join(sys.path[0], "credentials.json"), "r") as f:
        data = json.load(f)
        print(data)

    reddit = praw.Reddit(
                    client_id=data['client_id'],
                    client_secret=data['api_key'],
                    password=data['password'],
                    user_agent='<reddit_top> accessAPI:v0.0.1 (by/u/imagedownloaderuwu)',
                    username=data['username']
    )

    subreddit = reddit.subreddit("furry")

    name = 0

    for sub in subreddit.hot(limit=100):
        

        if name == amount:
            break
        else:
            url = (sub.url)
            if not url.endswith(tuple(ext)):
                continue
            name += 1

            r = requests.get(url)
            with open(os.path.join(path,str(name)+".png"), "wb") as f:
                f.write(r.content)

DownloadImages(50)
