# AI 每日资讯推送 Agent

自动抓取国内可访问的 AI 资讯源 + arXiv 论文，用 DeepSeek 生成中文简报，每天早上推送到邮箱/微信。

## 为什么做这个

备考期间保持 AI 领域敏感度，同时为复试积累一个真实的 AI 项目：
- 技术栈：Python + 数据抓取 + LLM 摘要 + 定时任务 + 多渠道推送
- 每天 15 分钟浏览即可"在场"，不占用主线备考时间

## 功能

- 抓取来源：量子位、新智元、IT之家AI、arXiv（cs.AI/cs.LG/cs.CL）
- LLM 摘要：DeepSeek 自动筛选 3-6 条最有价值的资讯，生成中文简报
- 推送渠道：邮件（SMTP）/ 微信（PushPlus）
- 定时运行：每天 7:30（避开 8-12、14-18 高峰），可自定义

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制配置模板并填写（config.py 不会上传到 GitHub，需自己创建）
copy config.example.py config.py     # Windows
# cp config.example.py config.py      # Linux/macOS
# 然后编辑 config.py，必填：
#    - 邮箱授权码（推荐）：MAIL_AUTH_CODE
#    - 或 PushPlus token（微信推送）
#    - DeepSeek API Key（不填也能用，只是不总结）

# 3. 测试抓取（不发送）
python main.py --source

# 4. 立即运行一次
python main.py

# 5. 常驻定时（每天7:30自动跑）
python main.py --daemon
```

## 配置说明（config.py）

| 配置项 | 说明 |
|--------|------|
| MAIL_SMTP_HOST/PORT | QQ邮箱 smtp.qq.com:465；163 smtp.163.com:465 |
| MAIL_AUTH_CODE | 邮箱授权码，不是登录密码！QQ邮箱在设置-账户-SMTP里开启 |
| PUSHPLUS_TOKEN | 微信扫码 https://www.pushplus.plus 登录后获取 |
| DEEPSEEK_API_KEY | https://platform.deepseek.com 创建，费用极低 |
| ARXIV_ENABLED | arXiv 国内一般可直连，如不行设 False |

## Windows 开机自启（可选）

常驻模式需要窗口一直开着。若想开机自动运行：
1. 新建 `start_digest.bat`：
```bat
@echo off
cd /d 本文件所在目录
python main.py --daemon
```
2. 按 `Win+R` 输入 `shell:startup` 回车，把 bat 放进去

## 项目结构

```
ai_daily_digest/
├── config.example.py # 配置模板：复制为 config.py 后填写（别人 clone 后从这里开始）
├── config.py         # 你的真实配置（已被 .gitignore 排除，不会上传）
├── main.py           # 主程序（抓取→总结→推送）
├── requirements.txt
└── README.md
```

## 项目结构说明

- `main.py --source` 只测抓取不发送；`main.py` 立即运行；`main.py --daemon` 常驻定时
- 各来源独立容错：机器之心/36氪因 JS 渲染已移除，换用量子位+新智元+IT之家+arXiv

## 免责声明

- 各网站页面结构可能改版，若某来源失效，检查 main.py 中对应函数的解析逻辑
- arXiv API 稳定，但如遇网络问题会自动跳过，不影响其他来源
- 本项目仅用于个人学习与信息获取
