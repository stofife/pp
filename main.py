import os
import json
import requests
import praw
import numpy as np
from PIL import Image

def DownloadImages(subreddit_name: str, amount: int, folder: str = "reddit", ext: list = [".jpg",".png"]) -> None:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    if not os.path.exists(__location__ + "\\" + folder):
        os.makedirs(__location__ + "\\" + folder)
   
    path = __location__ + "\\" + folder
    
    url = "https://www.reddit.com/"

    with open(os.path.join(__location__, "credentials.json"), "r") as f:
        data = json.load(f)

    reddit = praw.Reddit(
                    client_id=data['client_id'],
                    client_secret=data['api_key'],
                    password=data['password'],
                    user_agent='<reddit_top> accessAPI:v0.0.1 (by/u/imagedownloaderuwu)',
                    username=data['username']
    )

    subreddit = reddit.subreddit(subreddit_name)

    count = 0

    for sub in subreddit.hot(limit=amount*2):
        if count == amount:
            break
        else:
            url = (sub.url)
            if not url.endswith(tuple(ext)):
                continue
            count += 1
            r = requests.get(url)
            with open(os.path.join(path,str(count)+".png"), "wb") as f:
                f.write(r.content)
 
def cwd(): return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def DeleteImages(folder):

    loc = cwd() + "\\" + folder

    amount = len([name for name in os.listdir(loc) if os.path.isfile(loc + '\\' + name)]) + 1

    # Uncomment this when debugging ;3
    # print("Deleting the contents of: " + folder)

    for file in range(amount):
        if os.path.exists(loc + '\\' + str(file) + ".png"):
            os.remove(loc + '\\' + str(file) + ".png")
            # Uncomment this when debugging ;3
            #print("Successfully deleted: " + str(file) + ".png")


def ResizeImage(name, nw, nh, folder, newfolder = "resized"):

    if not os.path.exists(cwd() + "\\" + newfolder):
        os.makedirs(cwd() + "\\" + newfolder)

    img = Image.open(cwd() + "\\" + folder + "\\" + name + ".png")

    img = img.resize((nw, nh), Image.BICUBIC)

    img.save(cwd() + "\\" + newfolder + "\\" + name + ".png")
    # Uncomment this when debugging ;3
    #print("Image was resized and saved to: " + cwd() + "\\" + newfolder)


def RGBtoArray(name: str, folder = "resized"):

    img = Image.open(cwd() + "\\" + folder + "\\" + name + ".png")

    return np.asarray(img)


def GenerateFeatureMap(array, is3d = False):
    if is3d != False:
        slice = array[:, :, 1]
        print(slice.shape)


ResizeImage(str(1), 120, 90, "samples")
w = RGBtoArray(str(1), "resized")
print(w.shape)
GenerateFeatureMap(w, True)
#DownloadImages("furry", 10)
#for i in range(10):
#   ResizeImage(str(i+1), 120, 90, "reddit")
#DeleteImages("reddit")