
Ran tool

Ran tool

Ran tool

Ran tool

Ran tool

Ran tool

Ran tool

Ran tool

Ran tool

Read file: app.py

Read file: weibo_spider.py

Read file: database.py

Read file: data_analysis.py

Read file: storage.py

Read file: docs/database_design.md

Read file: config.py

Read file: utils/data_loader.py

Ran tool

Read file: templates/index.html
我已全面梳理了你的项目结构、主要代码、数据库设计和前端页面。下面为你撰写一份完整详细的项目文档，内容涵盖项目简介、功能说明、目录结构、依赖环境、核心模块说明、数据库设计、前端说明、运行方式、常见问题等。你可将其保存为 `README.md` 或 `docs/项目说明.md`。

---

# 微博热搜实时采集与分析系统

## 项目简介

本项目实现了对微博热搜榜单及话题详情的自动化采集、存储、分析与可视化。系统基于 Flask 提供 Web 服务，定时采集微博热搜数据，支持数据持久化、趋势分析、报表生成，并通过 ECharts 实现前端实时热度可视化。

## 主要功能

- 实时采集微博热搜榜单及话题详情
- 数据自动存储至 SQLite 数据库
- 热搜与话题数据的多维度分析与报表导出
- 提供 RESTful API 供前端/第三方调用
- 前端可视化展示热搜榜单及热度趋势
- 定时任务自动运行，支持日志记录与异常处理

## 目录结构

```
├── app.py                  # Flask主程序入口，路由与定时任务
├── weibo_spider.py         # 微博热搜与话题采集核心模块
├── data_analysis.py        # 数据分析与报表生成
├── storage.py              # 数据存储与加载
├── database.py             # ORM模型与数据库初始化
├── config.py               # 配置文件（API地址、请求头等）
├── utils/
│   └── data_loader.py      # 通用数据加载工具
├── data/                   # 数据文件存储目录
├── static/                 # 静态资源目录
├── templates/
│   └── index.html          # 前端页面模板
├── docs/
│   └── database_design.md  # 数据库设计文档
├── hotsearch.db            # SQLite数据库文件
├── spider_error.log        # 日志文件
```

## 依赖环境

- Python 3.7+
- Flask
- SQLAlchemy
- APScheduler
- requests
- ECharts（前端CDN加载）

安装依赖：
```bash
pip install flask sqlalchemy apscheduler requests
```

## 配置说明

编辑 `config.py`，配置微博API地址和请求头（需替换为有效的Cookie）：

```python
HOT_SEARCH_URL = 'https://weibo.com/ajax/side/hotSearch'
HEADERS = {
    'User-Agent': 'xxx',
    'Cookie': '替换为你的Cookie'
}
```

## 核心模块说明

### 1. app.py

- 启动 Flask Web 服务，注册路由
- 提供 `/api/hot-searches` 和 `/api/hot-searches/chart` 接口
- 启动 APScheduler 定时任务，定时采集热搜和话题详情

### 2. weibo_spider.py

- `get_weibo_hot_search()`：实时获取微博热搜榜单
- `get_weibo_topic_detail(keyword)`：获取指定话题详情
- `batch_get_topic_details(keywords)`：并发批量采集话题详情
- `save_hot_searches()`：采集并存储热搜数据
- `load_keywords(filename)`：加载关键词列表

### 3. storage.py

- `save_data()`：保存数据到JSON和数据库
- `save_topic_detail()`：保存话题详情到数据库
- `load_topic_details()`/`load_hot_searches()`：加载本地数据文件
- `load_data()`：自动识别并加载数据

### 4. data_analysis.py

- `WeiboDataAnalyzer`：话题详情分析，提取基础指标与趋势，生成分析报告
- `WeiboHotSearchAnalyzer`：热搜榜单分析，生成热搜报表

### 5. database.py

- 定义 `HotSearchRecord` 和 `TopicDetailRecord` 两张表的ORM模型
- 自动建表，支持热搜与话题详情的结构化存储

### 6. 前端页面（templates/index.html）

- 使用 ECharts 展示热搜榜单热度柱状图
- 定时轮询后端API，实时刷新数据
- 响应式美观UI，适配深色模式

## 数据库设计

详见 `docs/database_design.md`，主要表结构如下：

- **hot_searches**：存储热搜关键词、排名、热度、时间戳
- **topic_details**：存储话题关键词、分类、阅读量、讨论量、互动量、原创量、24h/30d趋势等

支持高效索引、分区归档、时序分析。

## 运行方式

1. 配置好 `config.py` 的请求头和Cookie
2. 启动主程序
   ```bash
   python app.py
   ```
3. 浏览器访问 [http://localhost:5000](http://localhost:5000) 查看实时热搜可视化页面

## 常见问题

- **Cookie失效/未配置**：需抓包获取有效Cookie，否则采集接口会失败
- **数据库文件权限**：确保有写入 `hotsearch.db` 的权限
- **API变更**：如微博接口变动，需调整 `HOT_SEARCH_URL` 和解析逻辑
- **定时任务未执行**：检查日志输出，确认APScheduler是否正常启动

## 日志与报错

- 日志输出至控制台及 `spider_error.log`
- 采集、存储、分析等异常均有详细日志，便于排查

## 贡献与扩展

- 支持自定义采集关键词、采集频率
- 可扩展更多分析维度与可视化页面
- 欢迎PR和建议！

---

如需更详细的API、数据结构或二次开发说明，可补充具体需求。

### 话题分类接口
GET `/api/topic-categories`
返回格式：
{
  "categories": [
    {"name": "娱乐", "value": 23},
    {"name": "社会", "value": 17}
  ]
}
