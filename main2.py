import io
import os
import copy
import json
import requests
import itertools
import concurrent.futures


import numpy as np
from PIL import Image
from collections.abc import Sequence
from typing import List, Tuple, Dict, Any

import praw

class OptionsError(Exception):
    def __init__(self, _dict: Dict[str,str]):
        self.message = "No (valid) options were provided"
        self._dict = _dict
        super().__init__(self.message)
    def __str__(self):
        return f"{self.message}. Recieved: {json.dumps(self._dict)}"

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

structure = {
    "results": os.path.join(__location__,"output"),
    "samples": os.path.join(__location__,"samples"),
    "credentials": os.path.join(__location__,"credentials.json")
}

def prepare(subreddit_name: str, amount: int, ext: Sequence[str] = [".jpg",".png"], url: str = "https://www.reddit.com/", maximum_threads: int = 5) -> List[io.BytesIO]:
    with open(structure["credentials"], "r") as f:
        credentials = json.load(f)
    
    reddit = praw.Reddit(client_id=credentials['client_id'], client_secret=credentials['api_key'], password=credentials['password'], user_agent='<reddit_top> accessAPI:v0.0.1 (by/u/imagedownloaderuwu)', username=credentials['username'])

    links = []

    subreddit = reddit.subreddit(subreddit_name)
    for post in subreddit.hot(limit=amount*2):
        if post.url.endswith(tuple(ext)):
            links.append(post.url)
        if len(links) > amount:
            break

    links = [list(i) for i in np.array_split(links, maximum_threads)] #divide list into smaller chunks
    """
    #alternate method
    chunks_size = len(links) // maximum_threads
    links = [links[i * chunks_size:(i + 1) * chunks_size] for i in range((len(links) + chunks_size - 1) // chunks_size)] #divide list into smaller chunks
    """
    result: Sequence[io.BytesIO] = []
    original: Sequence[io.BytesIO] = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for urls in links:
            futures.append(executor.submit(get_images, links=urls))
        for future in concurrent.futures.as_completed(futures):
            result.append(future.result()[0])
            original.append(future.result()[1])

    result = list(itertools.chain.from_iterable(result))
    original = list(itertools.chain.from_iterable(original))

    return (result,original)

def get_images(links: Sequence[str], resize: bool = True, new_dim: Tuple[int,int] = (120,120)) -> List[io.BytesIO]:
    result = []
    for url in links:
        response = requests.get(url)
        result.append(io.BytesIO(response.content))

    if resize:
        original = copy.deepcopy(result)
        for i in range(len(result)):
            img = Image.open(result[i])
            img = img.resize(new_dim, Image.BICUBIC)
            out = io.BytesIO()
            img.save(out,"png")
            result[i] = out
        return (result,original)

    return (result,[])

def get_samples(ext: Sequence[str] = [".jpg",".png"], resize: bool = True, new_dim: Tuple[int,int] = (120,120)) -> List[io.BytesIO]:
    result = []
    for file in [f for f in os.listdir(structure["samples"]) if os.path.isfile(os.path.join(structure["samples"], f))]:
        if not file.endswith(tuple(ext)):
            continue
        with open(os.path.join(structure["samples"],file), "rb") as f:
            result.append(io.BytesIO(f.read()))

        if resize:
            for i in range(len(result)):
                img = Image.open(result[i])
                img = img.resize(new_dim, Image.BICUBIC)
                out = io.BytesIO()
                img.save(out,"png")
                result[i] = out

    return result

def img_to_array(image: io.BytesIO, rm_alpha: bool = True) -> np.ndarray:
    img = Image.open(image)
    result = np.asarray(img).transpose(2,0,1)
    if rm_alpha and result.shape[0] > 3:
        result = np.delete(result,3,axis=0)

    return result

def slice_array(array: np.ndarray, dimnum: int) -> np.ndarray:

    return array[dimnum, :, :]

def pixel_pooling(array: np.ndarray, pooldim: int, **kwargs: Dict[str,str]) -> np.ndarray:
    def avgpool(array, pooldim: int):
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
    
    try:
        if kwargs["options"].upper() in ["AVERAGE","AVG"]:
            output = []
            for dimension in range(array.shape[0]):
                s = slice_array(array, dimension)
                output.append(avgpool(s, pooldim))
            return np.asarray(output)
    except KeyError:
        raise OptionsError(kwargs)

def cos_sim(vector1: int, vector2: int) -> float:
    return np.dot(vector1, vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))

def compare(images: Sequence[io.BytesIO], samples: Sequence[io.BytesIO],labels: Sequence[Any], similarity: int, original: Sequence[io.BytesIO]) -> None:
    count = 0
    for b_img in range(len(images)):
        avg_sim = 0
        new_pooled = pixel_pooling(img_to_array(images[b_img]), 3, options="avg").flatten()
        for b_sample_img in samples:
            sample_pooled = pixel_pooling(img_to_array(b_sample_img), 3, options="avg").flatten()
            avg_sim = avg_sim + cos_sim(sample_pooled, new_pooled)
        avg_sim = avg_sim / len(samples) * 100
        if avg_sim >= similarity:
            with open(os.path.join(structure["results"],str(labels[count])+".png"),"wb") as f:
                f.write(original[b_img].getvalue())
            count = count + 1
def main(*args,**kwargs) -> None:

    if not os.path.exists(structure["results"]):
        os.makedirs(structure["results"])

    similarity = int(input("Similarity?"))

    images, original = prepare("hentai",50)
    samples = get_samples()
    max_pools = 5
    labels = list(range(1,len(images)+1))
    labels = [list(i) for i in np.array_split(labels, max_pools)]
    images = [list(i) for i in np.array_split(images, max_pools)] #divide list into smaller chunks
    original = [list(i) for i in np.array_split(original, max_pools)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for index in range(len(images)):
            executor.submit(compare, images=images[index], samples=samples, labels=labels[index], similarity=similarity, original=original[index])

if __name__ == "__main__":
    main()
