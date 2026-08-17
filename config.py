# -*- coding: utf-8 -*-
"""
config.py - AI 每日资讯推送 · 配置文件
=====================================
所有需要你修改的配置都放在这里。照着注释填即可。
"""

# ==================== 1. 推送渠道（二选一或都填） ====================

# 方式A：邮件推送（推荐，最简单）
# QQ邮箱：在QQ邮箱网页版「设置-账户-开启SMTP服务」获取授权码（不是QQ密码！）
MAIL_ENABLED = True
MAIL_SMTP_HOST = "smtp.qq.com"          # QQ邮箱用 smtp.qq.com；163用 smtp.163.com
MAIL_SMTP_PORT = 465                    # 465(SSL) 或 587(TLS)
MAIL_USER = "你的QQ邮箱@qq.com"          # 发件邮箱(占位符，不用填写)
MAIL_AUTH_CODE = ""            # 授权码（SMTP密码）
MAIL_TO = "你的QQ邮箱@qq.com"              # 收件邮箱（可填自己，也可以和别人不同）

# 方式B：微信推送（通过 PushPlus 公众号，免费）
# 1. 打开 https://www.pushplus.plus/ 用微信扫码登录
# 2. 登录后主页显示你的 token（一串字符），填到下面
WECHAT_ENABLED = False
PUSHPLUS_TOKEN = ""

# ==================== 2. LLM 摘要（DeepSeek） ====================

# 在 https://platform.deepseek.com 注册并创建 API Key（费用极低，约0.001元/千token）
DEEPSEEK_API_KEY = ""
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"        # 若你的账号可用 deepseek-v4-flash 则填这个

# 没填 API Key 时：直接推送原始标题列表（不总结，仍可用）
# 填了 API Key 时：自动生成中文简报

# ==================== 3. 抓取设置 ====================

# 抓取时的浏览器标识
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0 Safari/537.36")

# 每个来源最多取几条
MAX_PER_SOURCE = 6

# arXiv 论文设置（国内一般可直接访问，如不行可设 False 关闭）
ARXIV_ENABLED = True
ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL"]   # AI/机器学习/自然语言
ARXIV_MAX_PAPERS = 5

# 连接超时（秒）
TIMEOUT = 15

# ==================== 4. 输出设置 ====================

# 调试模式：True 时不实际发送，只把内容打印到控制台
DEBUG = False
