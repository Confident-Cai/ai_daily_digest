# -*- coding: utf-8 -*-
"""
main.py - AI 每日资讯推送 · 主程序
==================================
功能：抓取国内可访问的 AI 资讯源 + arXiv 论文 -> DeepSeek 生成中文简报 -> 邮件/微信推送

用法：
    python main.py                 # 立即运行一次
    python main.py --daemon        # 常驻后台，每天按配置时间自动运行

首次使用：先编辑 config.py 填入邮箱/API Key，再运行。
"""

import argparse
import json
import smtplib
import time
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from urllib import request as urlreq

import requests
from bs4 import BeautifulSoup

import config

# ============================================================
# 一、数据源抓取（每个源独立 try/except，一个挂了不影响其他）
# ============================================================

HEADERS = {"User-Agent": config.USER_AGENT}


def _safe_get(url):
    """带超时和UA的GET请求，失败返回None"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=config.TIMEOUT)
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp
    except Exception as e:
        print(f"[警告] 抓取失败 {url}: {e}")
        return None


def fetch_jiqizhixin():
    """机器之心 - 首页最新文章（标题+链接）"""
    resp = _safe_get("https://www.jiqizhixin.com/")
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if title and href and len(title) >= 8 and "/articles/" in href:
            url = href if href.startswith("http") else "https://www.jiqizhixin.com" + href
            items.append(("机器之心", title, url))
            if len(items) >= config.MAX_PER_SOURCE:
                break
    return items


def fetch_qbitai():
    """量子位 - 首页文章"""
    resp = _safe_get("https://www.qbitai.com/")
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if title and href and len(title) >= 8 and href.startswith("http") and "qbitai.com" in href:
            items.append(("量子位", title, href))
            if len(items) >= config.MAX_PER_SOURCE:
                break
    return items


def fetch_aiera():
    """新智元 - 首页文章"""
    resp = _safe_get("https://www.aiera.com.cn/")
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        if title and len(title) >= 12:
            url = href if href.startswith("http") else "https://www.aiera.com.cn" + href
            items.append(("新智元", title, url))
            if len(items) >= config.MAX_PER_SOURCE:
                break
    return items


def fetch_ithome_ai():
    """IT之家 - 首页（AI 相关标题）"""
    resp = _safe_get("https://www.ithome.com/")
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if (title and href and len(title) >= 10
                and any(k in title for k in ("AI", "智能", "模型", "芯片", "机器人", "大模型"))):
            url = href if href.startswith("http") else "https://www.ithome.com" + href
            items.append(("IT之家", title, url))
            if len(items) >= config.MAX_PER_SOURCE:
                break
    return items


def fetch_arxiv():
    """arXiv - 当日新论文（cs.AI / cs.LG / cs.CL），返回标题+链接"""
    if not config.ARXIV_ENABLED:
        return []
    items = []
    for cat in config.ARXIV_CATEGORIES:
        url = ("http://export.arxiv.org/api/query"
               f"?search_query=cat:{cat}"
               "&sortBy=submittedDate&sortOrder=descending"
               f"&max_results={config.ARXIV_MAX_PAPERS}")
        resp = _safe_get(url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "xml")
        for entry in soup.find_all("entry"):
            title = entry.title.get_text(strip=True).replace("\n", " ")
            link = entry.id.get_text(strip=True) if entry.id else ""
            if title:
                items.append((f"arXiv/{cat}", title[:80], link))
    return items


def fetch_all():
    """抓取所有源，合并去重"""
    sources = [fetch_qbitai, fetch_aiera, fetch_ithome_ai, fetch_arxiv]
    all_items = []
    seen = set()
    for fn in sources:
        try:
            for item in fn():
                key = item[1]
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
        except Exception as e:
            print(f"[警告] {fn.__name__} 失败: {e}")
    print(f"[信息] 共抓取 {len(all_items)} 条")
    return all_items


# ============================================================
# 二、DeepSeek 生成中文简报
# ============================================================

def summarize(items):
    """用 DeepSeek 把条目整理成中文简报；无 Key 时降级为标题列表"""
    if not config.DEEPSEEK_API_KEY:
        lines = []
        for source, title, url in items:
            lines.append(f"- [{source}] {title}\n  {url}")
        return "（未配置 DeepSeek API Key，以下为原始列表）\n\n" + "\n".join(lines)

    text = "\n".join(f"[{s}] {t} | {u}" for s, t, u in items)
    prompt = (
        "你是AI领域资讯编辑。下面是我抓取到的当日AI资讯（来源|标题|链接），"
        "请筛选出3-6条最有价值的信息，生成一份中文简报，格式：\n"
        "## 今日AI简报\n"
        "1. 【标题】\n一句话说明事件\n值得关注：为什么重要\n（附原文链接）\n"
        "按重要程度排序，如果某类信息过时或重复可以合并。只输出简报本身。\n\n"
        f"资讯列表：\n{text}"
    )
    try:
        resp = requests.post(
            f"{config.DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[警告] DeepSeek 调用失败: {e}")
        lines = [f"- [{s}] {t}\n  {u}" for s, t, u in items]
        return "（DeepSeek 调用失败，降级为原始列表）\n\n" + "\n".join(lines)


# ============================================================
# 三、推送（邮件 / 微信）
# ============================================================

def build_message(body):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"【AI 每日资讯】{today}\n\n{body}\n\n—— 来自你的 AI 资讯推送 Agent"


def send_email(body):
    """QQ/163 邮箱 SMTP 推送"""
    if not config.MAIL_ENABLED:
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(f"AI每日资讯 {datetime.now().strftime('%m-%d')}", "utf-8")
        msg["From"] = config.MAIL_USER
        msg["To"] = config.MAIL_TO
        server = smtplib.SMTP_SSL(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT, timeout=30)
        server.login(config.MAIL_USER, config.MAIL_AUTH_CODE)
        server.sendmail(config.MAIL_USER, [config.MAIL_TO], msg.as_string())
        server.quit()
        print("[信息] 邮件发送成功")
        return True
    except Exception as e:
        print(f"[警告] 邮件发送失败: {e}")
        return False


def send_wechat(body):
    """PushPlus 微信推送"""
    if not config.WECHAT_ENABLED:
        return False
    try:
        resp = requests.post(
            "http://www.pushplus.plus/send",
            json={"token": config.PUSHPLUS_TOKEN,
                  "title": f"AI每日资讯 {datetime.now().strftime('%m-%d')}",
                  "content": body},
            timeout=30,
        )
        print(f"[信息] 微信推送结果: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[警告] 微信推送失败: {e}")
        return False


# ============================================================
# 四、主流程
# ============================================================

def run_once():
    print(f"[{datetime.now():%H:%M:%S}] 开始抓取...")
    items = fetch_all()
    if not items:
        print("[警告] 没有抓到任何内容，本次跳过")
        return
    body = build_message(summarize(items))
    if config.DEBUG:
        print("=" * 50)
        print(body)
        print("=" * 50)
        return
    ok_mail = send_email(body)
    ok_wx = send_wechat(body)
    if not ok_mail and not ok_wx:
        print("[警告] 两个推送渠道都失败了，请检查 config.py")


def run_daemon():
    """常驻模式：每天在配置的空闲时段运行（默认 7:30，避开 8-12/14-18 高峰）"""
    from schedule import every, run_pending  # 延迟导入，不跑daemon就不需要schedule
    hour, minute = 7, 30
    every().day.at(f"{hour:02d}:{minute:02d}").do(run_once)
    print(f"[信息] 已启动常驻，每天 {hour:02d}:{minute:02d} 自动运行（可改 main.py 末尾）")
    while True:
        run_pending()
        time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 每日资讯推送")
    parser.add_argument("--daemon", action="store_true", help="常驻模式，每天定时运行")
    parser.add_argument("--source", action="store_true", help="仅测试抓取，不发送")
    args = parser.parse_args()

    if args.source:
        items = fetch_all()
        for s, t, u in items:
            print(f"[{s}] {t}\n  {u}")
    elif args.daemon:
        run_daemon()
    else:
        run_once()
