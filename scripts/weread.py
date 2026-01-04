import os
import requests
from notion_client import Client

# 获取环境变量
cookie = os.getenv("WEREAD_COOKIE")
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("DATABASE_ID")

# 初始化 Notion 客户端
notion = Client(auth=notion_token)

# 获取微信读书书架
headers = {"Cookie": cookie}
shelf_url = "https://i.weread.qq.com/shelf/friendShelf?userVid=0"
resp = requests.get(shelf_url, headers=headers)
if resp.status_code != 200:
    raise Exception("微信读书 Cookie 无效或请求失败")

books = resp.json().get("books", [])
print(f"共找到 {len(books)} 本书")

for book in books[:3]:  # 先同步最近 3 本测试
    title = book["bookInfo"]["title"]
    author = book["bookInfo"].get("author", "")
    cover = book["bookInfo"].get("cover", "")
    progress = book.get("readingProgress", {}).get("totalReadCount", 0)
    total_pages = book["bookInfo"].get("pageCount", 1) or 1

    # 检查是否已存在
    results = notion.databases.query(
        database_id=database_id,
        filter={"property": "Book Title", "title": {"equals": title}}
    ).get("results")

    if results:
        page_id = results[0]["id"]
        notion.pages.update(
            page_id=page_id,
            properties={
                "Progress": {"number": progress},
                "Total Pages": {"number": total_pages},
                "Last Read": {"date": {"start": "2026-01-04"}},
            }
        )
        print(f"✅ 更新: {title}")
    else:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Book Title": {"title": [{"text": {"content": title}}]},
                "Author": {"rich_text": [{"text": {"content": author}}]},
                "Progress": {"number": progress},
                "Total Pages": {"number": total_pages},
                "URL": {"url": f"https://weread.qq.com/web/bookDetail/{book['bookId']}"},
                "Last Read": {"date": {"start": "2026-01-04"}},
            }
        )
        print(f"🆕 新增: {title}")
