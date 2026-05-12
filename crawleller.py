import sys
import argparse
from collections import deque
from bs4 import BeautifulSoup
import urllib
from urllib.error import HTTPError,URLError
import requests
from urllib.parse import urlparse, urljoin, urldefrag, unquote

import re
import time
import gzip
from http.cookies import SimpleCookie
from playwright.sync_api import sync_playwright

n=-1
user_field = None
pass_field = None
testcookies_dict = {}
target_request    = None
captured ={}
captured_response = {}
login_data = {}
thinh = []
ht =-1
parsed_cookies = []
session = requests.Session()


captured ={}
captured_response = {}

Email = re.compile(r'(username|user|user_name|email|email_address|mail|login|login_id|loginid|account|account_name|member|member_id|userid|user_id|customer|customer_id)', re.I)
Password = re.compile(r'(password|pass|passwd|pwd|passcode|secret|user_password|login_password)', re.I)
user_selector = "input[type='email'], input[name*='email'], input[id*='email']"
pass_selector = "input[type='password'], input[name*='pass'], input[id*='pass']"
def domtree(tag):
	if getattr(tag, "name", None) is None:
		return ""
	result = f"<{tag.name}>"
	for x in tag.children:
		result += domtree(x)
	return result
def isurl(url):
		if "http" in url or "https" in url:
				return True
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

def is_valid_url(url):
	if url is None:   
		return False
	bad_chars = ["'", '"', "<", ">", "{", "}"]

	for c in bad_chars:
		if c in url:
			return False
	if url.startswith(("javascript:", "mailto:", "tel:", "data:")):
		return False
	return True        

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
parser.add_argument("-cre", action="store_true", help="Login with username/password")
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


if args.cre:
	username = input("Please provide your username: ")
	password = input("Please provide your password: ")
	loginurl = input("Please provide your website's login url (ex: https://www.thxy.com/login): ")

	try:
		res = session.get(loginurl, timeout=10)
	except requests.exceptions.RequestException as e:
		print("Network error:", e)
	bs = BeautifulSoup(res.text, "html.parser")
	inputs = bs.find_all("input")
	for inp in inputs:
		val = inp.get("id") or inp.get("name")
		if inp.get("id"):
			ht = 1
		if inp.get("name"):
			ht=0

		if Email.search(val):
			user_field = val

		if Password.search(val):
			pass_field = val
	zzz=com.split("www.")[1]
	domainname=zzz.split(".",1)[0]
	print(domainname)

	def handle_route(route):
		global target_request
		req = route.request

		if req.method == "POST" and domainname in req.url:
			if req.post_data is not None:
				decoded = unquote(req.post_data)
				if username in decoded and password in decoded:
					captured["method"]  = req.method
					captured["url"]     = req.url
					captured["headers"] = dict(req.headers)
					captured["body"]    = req.post_data
					target_request      = req

		route.continue_()

	def handle_response(res):
		global target_request
		global res_status
		if target_request and res.request == target_request:
			captured_response["status"]  = res.status
			captured_response["headers"] = dict(res.headers)
			try:
				captured_response["body"] = res.text()
			except Exception:
				captured_response["body"] = "(unreadable)"
			print("\n=== STARTING ===")
			res_status =res.status


	def get_cookies(x, username, password):
		with sync_playwright() as p:
			browser = p.firefox.launch(headless=True)
			context = browser.new_context()
			page = context.new_page()
			page.route("**/*", handle_route)
			page.on("response", handle_response)  

			page.goto(x)
			page.wait_for_load_state("networkidle")
			if ht == 1:
				page.fill(f"#{user_field}", username)

				page.fill(f"#{pass_field}", password)
			if ht == 0:
				page.fill(f"[name='{user_field}']",username)
				page.fill(f"[name='{pass_field}']",password)
			page.click("button[type='submit'], input[type='submit']")  
			page.wait_for_load_state("networkidle")

			
			cookies = context.cookies()
			browser.close()
				
			return cookies




	cookies = get_cookies(loginurl, username, password)
	cookies_dict = {c["name"]: c["value"] for c in cookies}
	cap_url = captured.get("url")
	cap_headers = dict(captured.get("headers", {}))
	cap_headers.pop("cookie", None)
	cap_headers.pop("content-length", None)
	cap_body = captured.get("body")
	session = requests.Session()
	for c in cookies:
		session.cookies.set(
			c["name"],
			c["value"],
			domain=c.get("domain"),
			path=c.get("path")
		)
	response = session.post(
		cap_url,
		headers=cap_headers,
		data=cap_body,
		allow_redirects=False,   
	)
	print(response.status_code)



headers = {
	"User-Agent": "Mozilla/5.0",
	"Accept": "text/html",
	"Accept-Language": "en-US,en;q=0.9",
}

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
				if not args.cre:
					req = urllib.request.Request(x, headers=headers)
					time.sleep(0.3)
					response = urllib.request.urlopen(req)
					raw = response.read()
					try:
						raw = gzip.decompress(raw)
					except:
						pass
					html = raw.decode("utf-8", errors="ignore")
					bs = BeautifulSoup(html, "html.parser")
				if args.cre:
					req = session.get(x, headers=headers, timeout=10, allow_redirects=True)
					html = req.text
					bs = BeautifulSoup(html, "html.parser")
			except HTTPError as e:
				print(f"  [Error] {e.code}: {x}")
				continue
			except Exception as e:  
				print(f"  [Error] {e}: {x}")
				continue

			print(f"[Crawling] {x}")

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
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)

			for img in bs.find_all("img"):
				src = img.get("src")
				if not src:
					continue

				urll = urljoin(com, src)
				urll = remove_trailing_slash(urldefrag(urll).url)
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)

			for script in bs.find_all("script"):
				source = script.get("src")
				if not source:
					continue

				urll = urljoin(com, source)
				urll = remove_trailing_slash(urldefrag(urll).url)
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)

			for link in bs.find_all("link"):
				href2 = link.get("href")
				if not href2:
					continue

				urll = urljoin(com, href2)
				urll = remove_trailing_slash(urldefrag(urll).url)
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)

			for form in bs.find_all("form"):
				action = form.get("action")
				if not action:
					continue

				urll = urljoin(com, action)
				urll = remove_trailing_slash(urldefrag(urll).url)
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)

			for iframe in bs.find_all("iframe"):
				src3 = iframe.get("src")
				if not src3:
					continue

				urll = urljoin(com, src3)
				urll = remove_trailing_slash(urldefrag(urll).url)
				if not is_valid_url(urll):
					continue
				if samesite(urll, com) and urll not in visited and isurl(urll):
					newqueue.append(urll)


	print(f"\n--- Depth {k} done | URLs found: {len(newqueue)} ---\n")
	queue= newqueue
