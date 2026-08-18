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
- 定时运行：每天 12:30（避开 8-12、14-18 高峰），可自定义

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

# 5. 常驻定时（每天12:30自动跑，启动时会立即先跑一次）
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

## 常见问题（FAQ）

### 1. 运行报 `ModuleNotFoundError: No module named 'bs4'`
依赖未安装。先执行：
```bash
pip install -r requirements.txt
```
若 `pip` 不可用，改用 `python -m pip install -r requirements.txt`；下载慢可加清华镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 抓取报 `SSL: CERTIFICATE_VERIFY_FAILED`
部分 Python 环境缺少本地 CA 证书（Windows 常见），导致 HTTPS 请求全部失败。
本项目已内置处理：`main.py` 中 `SSL_VERIFY = False`，抓取公开资讯时跳过证书验证（个人项目通用做法）。无需额外操作。

### 3. 推送时间与高峰时段
DeepSeek API 采用峰谷定价：高峰 9:00-12:00、14:00-18:00，空闲时段价格减半。
本程序默认 12:30 推送（空闲时段），且 daemon 启动时会自动判断：
- 非高峰启动 → 立即执行一次
- 高峰启动（8-12/14-18）→ 顺延到高峰结束后再执行，节省 API 费用

### 4. 开机自启（Windows）
**推荐方式：Windows 任务计划程序（最可靠，360 不拦截）**
1. 在项目目录创建 `start_digest.bat`：
```bat
@echo off
cd /d "%~dp0"
start /min pythonw main.py --daemon
```
2. 按 `Win+R` 输入 `taskschd.msc` 回车，打开任务计划程序
3. 右侧"创建任务"：
   - 常规：名称 `AIDailyDigest`，**取消勾选"不管用户是否登录都要运行"**（否则报错 0x8004131F "占位程序接收到错误数据"）
   - 触发器：新建 → 开始任务选"**登录时**"
   - 操作：新建 → 启动程序，程序填 `pythonw`，**添加参数**填 `main.py --daemon`，**起始于**填项目目录（不要直接引用 bat，避免中文路径问题）
   - 条件：取消"只有交流电时启动"
   - 确定保存
4. 验证：右键任务 → "运行"，任务管理器出现 pythonw.exe 即成功

**备选方式：启动文件夹**
- 按 `Win+R` 输入 `shell:startup` 回车，把 `start_digest.bat` 复制进去
- ⚠️ 注意：360 安全卫士会拦截/自动删除放入启动文件夹的 .bat 文件，导致"文件消失"
- 此时改用：创建 bat 的**快捷方式**（.lnk）放入启动文件夹，360 一般不拦快捷方式

### 5. 常驻窗口关闭后不推送
`--daemon` 模式需要窗口一直开着。若使用开机自启的 bat，关闭窗口即停止；
若想长期稳定运行，建议配合 Windows 任务计划程序或保留窗口最小化。

### 6. 修改推送时间
`main.py` 末尾 `run_daemon()` 中修改：
```python
hour, minute = 12, 30   # 改为你想要的推送时间
```

### 7. 邮件内容为空（只有标题没有正文）
DeepSeek 为思考型模型（响应含 `reasoning_content`），推理过程会先占用 token 配额。
若 `max_tokens` 设置过小（如 2000），30 条资讯的长 prompt 会让推理吃光配额，导致最终答案（content）被截断为空。
**已修复**：`max_tokens` 提高至 4000，并增加空内容兜底（返回空时自动降级为原始标题列表，保证邮件永远有内容）。

### 8. 邮件发送卡住/超时（SMTP 反向 DNS 查询）
`smtplib` 连接时默认执行 `socket.getfqdn()` 反向 DNS 查询，部分网络环境下会卡住数分钟。
**已修复**：连接时显式指定 `local_hostname="localhost"` 跳过该查询：
```python
server = smtplib.SMTP_SSL(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT,
                          local_hostname="localhost", timeout=30)
```

### 9. 邮件报 `'ascii' codec can't encode` 编码错误
`config.py` 中邮箱地址填了中文占位符（如"你的QQ邮箱@qq.com"）导致 SMTP 编码失败。
**解决**：`MAIL_USER` / `MAIL_TO` 必须填真实邮箱（如 `3617066195@qq.com`），授权码填 SMTP 授权码（非QQ密码）。

### 10. 修改了代码后 daemon 还在用旧逻辑
daemon 是常驻进程，改完 `main.py` 需要**重启**才生效：先关掉旧窗口，重新运行 `python main.py --daemon`。

## 项目结构

## 项目结构说明

- `main.py --source` 只测抓取不发送；`main.py` 立即运行；`main.py --daemon` 常驻定时
- 各来源独立容错：机器之心/36氪因 JS 渲染已移除，换用量子位+新智元+IT之家+arXiv

## 免责声明

- 各网站页面结构可能改版，若某来源失效，检查 main.py 中对应函数的解析逻辑
- arXiv API 稳定，但如遇网络问题会自动跳过，不影响其他来源
- 本项目仅用于个人学习与信息获取
