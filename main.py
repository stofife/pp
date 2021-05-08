import os
import json
import requests
import praw
import numpy as np
from shutil import copy
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

    f = os.path.join(cwd(), folder)

    return len([name for name in os.listdir(f) if os.path.isfile(os.path.join(f, name))])


def DeleteImages(folder):

    loc = os.path.join(cwd(), folder)

    amount = FileCount(folder)
    # Uncomment this when debugging ;3 .
    # print("Deleting the contents of: " + folder)

    for file in range(1, amount + 1):
        if os.path.exists(os.path.join(loc, str(file) + ".png")):
            os.remove(os.path.join(loc, str(file) + ".png"))
            # Uncomment this when debugging ;3
            #print("Successfully deleted: " + str(file) + ".png")
    
    amount = FileCount(folder)

    if amount == 0:
        print("Successfully deleted all files in " + loc)


def ResizeImage(name: str, nw, nh, folder, newfolder = "resized"):

    if not os.path.exists(os.path.join(cwd(), newfolder)):
        os.makedirs(os.path.join(cwd(), newfolder))

    img = Image.open(os.path.join(cwd(), folder, name + ".png"))

    img = img.resize((nw, nh), Image.BICUBIC)

    img.save(os.path.join(cwd(), newfolder, name + ".png"))

    # Uncomment this when debugging ;3
    #print("Image was resized and saved to: " + os.path.join(cwd(), newfolder, name + ".png"))


def RGBtoArray(name: str, folder = "resized", removeAlpha = True):

    img = Image.open(os.path.join(cwd(), folder, name + ".png"))
    
    result = np.asarray(img).transpose(2,0,1)

    if removeAlpha == True and result.shape[0] > 3:
        result = np.delete(result, 3, axis=0)

    return result


def SliceArray(array, dimnum):

    return array[dimnum, :, :]


def PixelPooling(array, pooldim: int, option: str = "AVERAGE"):

    def avgpool(array, pooldim: int):
        #array must be 2D >///<
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


def CosineSimilarity(vector1, vector2):
    return np.dot(vector1, vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))


folder = "reddit"

samplesfolder = "samples"

found = []

if not os.path.exists(os.path.join(cwd(), "found")):
        os.makedirs(os.path.join(cwd(), "found"))


DownloadImages("furry", 30, folder)

sim = input("At least how similar do you want the pictures to be? (Press Enter to leave it at the default value): ")

if sim == "":
    sim = 70
else: 
    sim = int(sim)

for file in range(1, FileCount(folder) + 1):
    # Processing new image for comparison >w<
    ResizeImage(str(file), 120, 120, folder)
    newarray = RGBtoArray(str(file))
    newpooled = PixelPooling(newarray, 3).flatten()
    avgsim = 0

    # Processing liked images for comparison and calculating an average out of all sample comparisons owo
    for sample in range(1, FileCount(samplesfolder) + 1):
        ResizeImage(str(sample), 120, 120, samplesfolder, "resizedsamples")
        samplearray = RGBtoArray(str(sample), "resizedsamples")
        samplepooled = PixelPooling(samplearray, 3).flatten()
        avgsim += CosineSimilarity(samplepooled, newpooled)

    avgsim = avgsim/FileCount(samplesfolder)

    if avgsim >= sim/100:
        print(str(file) + ".png" + " is " + str(round(avgsim*100, 2)) + "%" + " similar to the pictures you like!")
        found.append(file)
        print("Copying file " + str(file) + ".png" + " to " + cwd() + "\\" + "found")
        copy(os.path.join(cwd(), folder, str(file) + ".png"), os.path.join(cwd(), "found", str(file) + ".png"))        

DeleteImages("resized")
DeleteImages("resizedsamples")
# Uncomment to see pooled images, tho beware cuz it opens each one in a new window uwu
#newpooled = Image.fromarray(newpooled, "RGB")
#newpooled.show()
