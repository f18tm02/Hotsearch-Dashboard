import multiprocessing

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'sync'

# 绑定地址
bind = '127.0.0.1:5000'

# 日志配置
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# 进程名称
proc_name = 'hotsearch'

# 超时时间
timeout = 30

# 最大请求数
max_requests = 2000
max_requests_jitter = 400 