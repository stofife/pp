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


def FileCount(folder):
    f = cwd() + "\\" + folder
    return len([name for name in os.listdir(f) if os.path.isfile(f + '\\' + name)]) + 1


def DeleteImages(folder):

    loc = cwd() + "\\" + folder

    amount = FileCount(folder)
    # Uncomment this when debugging ;3
    # print("Deleting the contents of: " + folder)

    for file in range(amount):
        if os.path.exists(loc + '\\' + str(file) + ".png"):
            os.remove(loc + '\\' + str(file) + ".png")
            # Uncomment this when debugging ;3
            #print("Successfully deleted: " + str(file) + ".png")


def ResizeImage(name: str, nw, nh, folder, newfolder = "resized"):

    if not os.path.exists(cwd() + "\\" + newfolder):
        os.makedirs(cwd() + "\\" + newfolder)

    img = Image.open(cwd() + "\\" + folder + "\\" + name + ".png")

    img = img.resize((nw, nh), Image.BICUBIC)

    img.save(cwd() + "\\" + newfolder + "\\" + name + ".png")

    # Uncomment this when debugging ;3
    print("Image was resized and saved to: " + cwd() + "\\" + newfolder + "\\" + name + ".png")


def RGBtoArray(name: str, folder = "resized"):

    img = Image.open(cwd() + "\\" + folder + "\\" + name + ".png")

    return np.asarray(img).transpose(2,0,1) 


def SliceArray(array, dimnum):

    return array[dimnum, :, :]


def PixelPooling(array, pooldim: int, option: str = "AVERAGE"):

    def avgpool(array, pooldim: int):
        #array must be 2D
        newarray = np.zeros((array.shape[0]//pooldim, array.shape[0]//pooldim), int)
        result = 0
        for column in range(array.shape[0]//pooldim):
            for r in range(array.shape[0]//pooldim):
                for a in range(pooldim):
                    for v in range(pooldim):
                        result += array[a + column * pooldim][v + r * pooldim]

                avg = result//(pooldim*pooldim)

                newarray[column][r] = avg

                result = 0

        return newarray

    if option == "AVERAGE":
        output = []
        for dimension in range(array.shape[0]):
            s = SliceArray(array, dimension)
            output.append(avgpool(s, pooldim))
        return np.asarray(output)


folder = "yiff"

#DownloadImages("yiff", 20, folder)

#for file in range(1, FileCount(folder)):
for file in range(1, 2):
    ResizeImage(str(file), 120, 120, folder)
    colorarray = RGBtoArray(str(file))
    print(colorarray.shape)
    pooled = PixelPooling(colorarray, 3)
    print(pooled.shape)
