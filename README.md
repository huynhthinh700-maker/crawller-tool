# 🕷️ Crawleller - Simple Web Crawler & DOM Analyzer

## 📌 Overview
**Crawleller** is a lightweight web crawler written in Python. It is designed to:

- Crawl websites using depth-based traversal (BFS)
- Extract internal URLs (same-domain only)
- Analyze and print DOM structure
- Filter elements by tag, class, id, or attribute
- Support custom HTTP headers (useful for authenticated crawling)

This tool is ideal for:
- Learning web crawling & scraping
- Building a foundation for security scanners
- Understanding website structure (similar to spider tools)

---

## ⚙️ Features

- 🔍 Depth-based crawling (`-d`)
- 🌐 Same-domain restriction
- 🧱 DOM tree visualization (`-dom`)
- 🎯 Element filtering:
  - `tag=`
  - `class=`
  - `id=`
  - `attr=`
- 🍪 Custom HTTP headers support (cookies, auth, etc.)
- 🔗 Extract links from:
  - `<a>`
  - `<img>`
  - `<script>`
  - `<link>`
  - `<form>`
  - `<iframe>`

---

## 🚀 Usage

### Basic crawl

```bash
python crawleller.py -domain http://example.com
Crawl with depth
python crawleller.py -domain http://example.com -d 3
Print DOM tree
python crawleller.py -domain http://example.com -dom
```
Filter elements
By tag
-f "tag=div"
By class
-f "class=container"
By id
-f "id=main"
By attribute
-f "attr=href"
Example
python crawleller.py -domain http://example.com -f "attr=href"

→ Prints all elements that contain href

## 🔐 Custom Headers (Authentication / Cookies)

You can provide a file with raw HTTP headers:

python crawleller.py -domain http://example.com -cre headers.txt
Example headers.txt
Cookie: session=abc123
Authorization: Bearer token123
## 🧠 How It Works

Uses BFS traversal with deque

Parses HTML using BeautifulSoup

Avoids duplicate crawling using set()

Normalizes URLs with:

urljoin

urldefrag

Filters same-domain URLs using urlparse

## 👨‍💻 Author
# THXY
