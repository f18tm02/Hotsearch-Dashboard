import json
from datetime import datetime
import os

def load_data(filename):
    '''
    通用数据加载方法（从storage.py迁移）
    
    参数:
        filename (str): 数据文件路径
    
    返回:
        dict: 加载的JSON数据
    
    异常:
        FileNotFoundError: 文件不存在时抛出
        JSONDecodeError: JSON解析失败时抛出
    '''
    file_path = os.path.join('data', filename) if not os.path.isabs(filename) else filename
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 添加时间戳验证
            if 'timestamp' in data:
                data['load_time'] = datetime.now().isoformat()
            return data
    except json.JSONDecodeError:
        raise ValueError(f"文件内容不是有效的JSON格式: {file_path}")