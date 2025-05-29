# 微博热搜大屏可视化平台部署指南

## 环境要求
- Python 3.8+ 
- Node.js 14+（仅前端构建需要）
- Windows PowerShell 5.1+

## 快速启动
```powershell
# 克隆仓库
git clone https://github.com/your_repo.git
cd 热搜3

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from database import init_db; init_db()"

# 启动爬虫（后台运行）
Start-Process python -ArgumentList "weibo_spider.py" -WindowStyle Hidden

# 启动可视化服务
flask run --port=5000 --host=0.0.0.0
```

## 完整部署流程
1. **数据采集**  
`> python weibo_spider.py --real-time`  
*每日0点自动归档数据*

2. **服务监控**  
```
# 查看后台进程
Get-Process python | Where-Object {$_.Path -like "*热搜3*"}

# 日志查看
Get-Content -Wait .\spider_error.log
```

3. **前端自定义**  
修改`templates/`目录下的HTML文件后：  
`Ctrl + F5` 强制刷新浏览器即可生效

## 常见问题
Q：地图显示不全？  
A：确认`china.json`文件在项目根目录

Q：数据更新延迟？  
A：检查后台爬虫进程是否正常运行

## 维护建议
- 每日备份`hotsearch.db`数据库
- 使用`nginx`反向代理实现外网访问
- 定期清理`data/`目录历史数据

---
📞 技术支持：2512709610@qq.com