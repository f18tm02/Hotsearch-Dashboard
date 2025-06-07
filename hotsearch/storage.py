import json
import os
from datetime import datetime
from database import Session, HotSearchRecord, TopicDetailRecord
from utils.data_loader import load_data
from data_analysis import WeiboDataAnalyzer
import logging

logger = logging.getLogger(__name__)

def save_data(data, filename):
    """
    保存数据到JSON文件并写入数据库
    :param data: 要保存的字典数据
    :param filename: 保存文件名（自动添加data目录路径）
    """
    logger.info(f'开始存储数据到 {filename}')
    # 原始文件存储
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 数据库存储
    session = Session()
    try:
        logger.info(f'准备写入数据库，数据条目数: {len(data.get("hot_searches", []))}')
        if 'hot_searches' in data:
            for item in data['hot_searches']:
                record = HotSearchRecord(
                    keyword=item['title'],
                    rank=item['rank'] + 1,
                    hot_value=item['hot_value'],
                    timestamp=datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
                )
                session.add(record)
        elif 'topic_data' in data:
            save_topic_detail(data, session)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"数据库存储失败: {str(e)}")
        raise e
    finally:
        session.close()

def save_topic_detail(data, session=None):
    """
    保存话题详情数据到数据库
    
    Args:
        data (dict): 包含话题详情的数据字典
        session (Session, optional): 数据库会话对象，如果为None则创建新会话
    
    Returns:
        bool: 保存是否成功
    """
    should_close_session = False
    if session is None:
        session = Session()
        should_close_session = True
    
    try:
        analyzer = WeiboDataAnalyzer(data)
        metrics = analyzer.extract_basic_metrics()
        trend = analyzer.extract_trend_data()
        
        record = TopicDetailRecord(
            keyword=data['keyword'],
            read_count=metrics['阅读量'],
            discuss_count=metrics['讨论量'],
            interact_count=metrics['互动量'],
            origin_count=metrics['原创量'],
            category=metrics['分类'],
            summary=metrics['摘要'],
            location=metrics['地域'],
            trend_24h=trend['24小时阅读增长'],
            trend_30d=trend['30天阅读总量'],
            timestamp=datetime.now()
        )
        session.add(record)
        
        if should_close_session:
            session.commit()
            #logger.info(f"成功保存话题 {data['keyword']} 的详情数据到数据库")
            return True
            
    except Exception as e:
        if should_close_session:
            session.rollback()
        logger.error(f"保存话题 {data.get('keyword', 'unknown')} 详情数据失败: {str(e)}")
        raise e
    finally:
        if should_close_session:
            session.close()

def load_topic_details(filename):
    """
    加载话题详情数据
    :param filename: 数据文件名
    :return: 话题详情字典数据
    """
    filepath = os.path.join('data', filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"话题详情文件不存在: {filepath}")
        return {'topic_data': {'baseInfo': {'count': {}, 'object': {'category_str': '未知'}}}}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data.get('topic_data', {}).get('baseInfo', {}).get('count'):
                logger.warning(f"话题数据缺少count字段: {filepath}")
                return {'topic_data': {'baseInfo': {'count': {}, 'object': {'category_str': '未知'}}}}
            return data
    except Exception as e:
        logger.error(f"加载话题详情数据失败: {str(e)}")
        return {'topic_data': {'baseInfo': {'count': {}, 'object': {'category_str': '未知'}}}}

def load_hot_searches(filename):
    """
    加载热搜榜单数据
    :param filename: 数据文件名
    :return: 热搜榜单字典数据
    """
    filepath = os.path.join('data', filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"热搜数据文件不存在: {filepath}")
        return {'hot_searches': []}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data.get('hot_searches'):
                logger.warning(f"热搜数据格式不完整: {filepath}")
                return {'hot_searches': []}
            return data
    except Exception as e:
        logger.error(f"加载热搜数据失败: {str(e)}")
        return {'hot_searches': []}

def load_data(filename):
    '''
    统一数据加载入口（自动路由）
    
    参数:
        filename (str): 数据文件路径，支持以下类型数据：
            - 话题详情数据：包含'topic_data.baseInfo.count'字段
            - 热搜榜单数据：包含'hot_searches'列表
    
    返回:
        dict: 自动识别的数据结构，可能是话题详情或热搜榜单
    '''
    try:
        # 先尝试加载为话题详情数据
        data = load_topic_details(filename)
        if data.get('topic_data', {}).get('baseInfo', {}).get('count'):
            return data
    except Exception as e:
        logger.warning(f"加载话题详情数据失败: {str(e)}")
    
    try:
        # 失败后尝试加载为热搜数据
        return load_hot_searches(filename)
    except Exception as e:
        logger.error(f"加载热搜数据失败: {str(e)}")
        return {'hot_searches': []}