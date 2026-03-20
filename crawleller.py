import sys
import argparse
from collections import deque
from bs4 import BeautifulSoup
import urllib
from urllib.error import HTTPError,URLError
import requests
from urllib.parse import urlparse, urljoin, urldefrag
import re
import time
n=-1
thinh = []
def domtree(tag):
    if getattr(tag, "name", None) is None:
        return ""
    result = f"<{tag.name}>"
    for x in tag.children:
        result += domtree(x)
    return result

def head(x):
    n =-1
    for k in x:
        n +=1
        if k == ":":
            header = x[:n]
            return header
def value(x):
    n =-1
    for k in x:
        n +=1
        if k == ":":
            value = x[n+2:]
            return value

def samesite(url, base):
    return urlparse(url).hostname == urlparse(base).hostname    

        

def remove_trailing_slash(url):

    if not url:
        return url

    if url.endswith('/'):
        url = url[:-1]

    return url


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.9",
}

print(sys.argv)
print("Please put your header in a double quotes without <> (ex: -f  \"h1\") ")


parser = argparse.ArgumentParser(description="Web crawler tool - crawls a website and extracts URLs")
parser.add_argument("-domain", type=str, help="URL to crawl (ex: http://localhost:8000)")
parser.add_argument("-d", type=int, default=6, help="Crawl depth (default: 6)")
parser.add_argument("-f", type=str, help="header selector (ex: class=container, id=main, tag=h1, attr=href)")
parser.add_argument("-cre", type=str, help="Path to credential file containing raw HTTP headers")
args = parser.parse_args()
depth = args.d
target = args.f
com = args.domain
file =args.cre

if target:
    if "tag=" not in target and "class=" not in target and "id=" not in target and "attr=" not in target and "tattr=" not in target:
        print("Invalid syntax")
        sys.exit()

        
    for tag in target:
        n = n+1

        if tag == "=":
            the = target[n+1:]
        

    if "class=" in target:
        thinh.append(".")
        for zz in the:
            thinh.append(zz)
    if "id=" in target:
        thinh.append("#")
        for zz in the:
            thinh.append(zz)
    if "attr" in target:
        thinh.append("[")
        for zz in the:
            thinh.append(zz)
        thinh.append("]")

    thed = "".join(thinh)

if file == None:
    headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.9",
    }
else:
    headers={}
    with open(file,"r")as file:
        for x in file.readlines():
            if ":" in x:
                x=x.strip()
                headers[head(x)] = value(x)


queue = deque([com])
visited = set()


for k in range(depth):
    k +=1
    
    print(k)
    newqueue = deque([])
    same = {}


    while queue:
            x = queue.popleft()

            if x in visited:
                continue
            visited.add(x)

            try:
                req = urllib.request.Request(x, headers=headers)
                time.sleep(0.7)
                response = urllib.request.urlopen(req)
                html = response.read().decode("utf-8", errors="ignore")
                bs = BeautifulSoup(html, "html.parser")
            except HTTPError as e:
                print(f"  [Error] {e.code}: {x}")
                continue

            print(f"[Crawling] {x}")
            visited.add(x)

            if target:
                results = bs.select(thed)
                for r in results:
                    print(f"  [filter:{thed}] {r.get_text(strip=True)}")

            fp = domtree(bs)
            same[fp] = same.get(fp, 0) + 1
            if same[fp] > 4:
                print(f"  [DOM skip] {x}")

            for a in bs.find_all("a"):
                href = a.get("href")
                if not href:
                    continue

                urll = urljoin(com, href)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)

            for img in bs.find_all("img"):
                src = img.get("src")
                if not src:
                    continue

                urll = urljoin(com, src)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)

            for script in bs.find_all("script"):
                source = script.get("src")
                if not source:
                    continue

                urll = urljoin(com, source)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)

            for link in bs.find_all("link"):
                href2 = link.get("href")
                if not href2:
                    continue

                urll = urljoin(com, href2)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)

            for form in bs.find_all("form"):
                action = form.get("action")
                if not action:
                    continue

                urll = urljoin(com, action)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)

            for iframe in bs.find_all("iframe"):
                src3 = iframe.get("src")
                if not src3:
                    continue

                urll = urljoin(com, src3)
                urll = remove_trailing_slash(urldefrag(urll).url)

                if samesite(urll, com) and urll not in visited:
                    newqueue.append(urll)


    print(f"\n--- Depth {k} done | URLs found: {len(newqueue)} ---\n")
    queue= newqueue
