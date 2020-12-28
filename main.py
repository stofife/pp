from unidecode import unidecode
import sys, os, shutil, unicodedata, json, praw, requests

def DownloadImages(amount):
    if not os.path.exists("reddit"):
        os.makedirs(sys.path[0] + '\\' + "reddit")

    path = str(sys.path[0] + '\\' + "reddit")
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
        name += 1

        if name == amount + 1:
            break
        else:
            url = (sub.url)
            file_name = str(name)
            if url.endswith(".jpg"):
                file_name += ".jpg"
                foundfile = True
            elif url.endswith(".png"):
                file_name += ".png"
                foundfile = True
            else:
                foundfile = False

            if foundfile == True:
                r = requests.get(url)
                with open(file_name, "wb") as f:
                    f.write(r.content)
                file_path = sys.path[0]
                file_path = file_path.replace('pp', '')
                shutil.move(file_path + file_name, path)

DownloadImages(50)