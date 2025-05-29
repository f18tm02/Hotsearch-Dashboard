import requests
import json
import urllib.parse
from datetime import datetime
from storage import save_data
from config import HEADERS, HOT_SEARCH_URL
import concurrent.futures
import time
import logging
import traceback
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

'''
微博热搜数据采集模块

该模块提供以下核心功能：
1. 实时获取微博热搜榜单（get_weibo_hot_search）
2. 获取指定话题的详细数据（get_weibo_topic_detail）
3. 自动数据持久化存储（save_hot_searches）

依赖配置：
- HOT_SEARCH_URL: 微博热搜API地址
- HEADERS: 请求头配置（需包含Cookie和User-Agent）
- SEARCH_KEYWORDS: 预设监控的关键词列表
'''

def get_weibo_hot_search():
    '''
    获取实时微博热搜榜单

    Returns:
        dict: {
            status: 请求状态（success/error）,
            data: {
                hot_searches: [{
                    rank: 排名,
                    title: 热搜标题,
                    hot_value: 热度值,
                    category: 分类,
                    timestamp: 采集时间戳
                }]
            }
        }

    Raises:
        RequestException: 网络请求异常
        JSONDecodeError: JSON解析失败
    '''
    try:
        response = requests.get(HOT_SEARCH_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        hot_items = response.json().get('data', {}).get('realtime', [])
        if not hot_items:
            logger.warning("热搜数据为空")
            return {'status': 'error', 'message': '热搜数据为空'}
            
        # 添加分类统计逻辑
        category_stats = {}
        for item in hot_items:
            category = item.get('category') or '其他'
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_hot': 0
                }
            category_stats[category]['count'] += 1
            category_stats[category]['total_hot'] += item.get('num', 0)

        return {
            'status': 'success',
            'data': {
                'hot_searches': [{
                    'rank': item.get('rank'),
                    'title': item.get('note'),
                    'hot_value': item.get('num'),
                    'category': item.get('category'),
                    'timestamp': datetime.now().isoformat()
                } for item in hot_items],
                'category_stats': [
                    {
                        'name': key,
                        'count': val['count'],
                        'total_hot': val['total_hot']
                    } for key, val in category_stats.items()
                ]
            }
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"热搜请求异常: {str(e)}")
        return {'status': 'error', 'message': f"请求错误: {str(e)}"}
    except json.JSONDecodeError as e:
        logger.error(f"热搜JSON解析失败: {str(e)}")
        return {'status': 'error', 'message': '无效的JSON响应'}
    except Exception as e:
        logger.error(f"热搜处理未知异常: {str(e)}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return {'status': 'error', 'message': f"未知错误: {str(e)}"}

def get_weibo_topic_detail(keyword: str, max_retries: int = 3) -> Dict[str, Any]:
    '''
    获取指定话题的详细数据（增加重试机制）

    Args:
        keyword (str): 需要查询的关键词
        max_retries (int): 最大重试次数

    Returns:
        dict: {
            status: 请求状态,
            data: {
                keyword: 查询关键词,
                topic_data: 话题详细数据
            }
        }
    '''
    for attempt in range(max_retries):
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            url = f'https://m.s.weibo.com/ajax_topic/detail?q={encoded_keyword}&show_rank_info=1'
            
            logger.info(f"正在获取话题 {keyword} 的详情数据 (尝试 {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            json_data = response.json()
            if not json_data.get('data'):
                logger.warning(f"话题 {keyword} 数据格式异常")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'status': 'error',
                    'message': '话题数据格式异常',
                    'keyword': keyword
                }
                
            return {
                'status': 'success',
                'data': {
                    'keyword': keyword,
                    'topic_data': json_data.get('data', {})
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"话题 {keyword} 第{attempt+1}次请求失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
            return {
                'status': 'error',
                'message': f"请求错误: {str(e)}",
                'keyword': keyword
            }
        except json.JSONDecodeError as e:
            logger.error(f"话题 {keyword} JSON解析失败: {str(e)}")
            return {
                'status': 'error',
                'message': '无效的JSON响应',
                'keyword': keyword
            }
        except Exception as e:
            logger.error(f"话题 {keyword} 处理异常: {str(e)}")
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            return {
                'status': 'error',
                'message': f"未知错误: {str(e)}",
                'keyword': keyword
            }

def batch_get_topic_details(keywords: List[str], max_workers: int = 3) -> List[Dict[str, Any]]:
    '''
    批量获取话题详情数据（并发处理）

    Args:
        keywords (List[str]): 关键词列表
        max_workers (int): 最大并发数

    Returns:
        List[Dict[str, Any]]: 话题详情数据列表
    '''
    if not keywords:
        logger.warning("没有提供关键词列表")
        return []
        
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_keyword = {
            executor.submit(get_weibo_topic_detail, keyword): keyword 
            for keyword in keywords
        }
        
        for future in concurrent.futures.as_completed(future_to_keyword):
            keyword = future_to_keyword[future]
            try:
                result = future.result()
                if result['status'] == 'success':
                    # 保存原始JSON数据
                    filename = f'weibo_{keyword}_data.json'
                    save_data(result['data'], filename)
                    logger.info(f"成功保存话题 {keyword} 的详情数据")
                else:
                    logger.warning(f"话题 {keyword} 采集失败: {result.get('message', '未知错误')}")
                results.append(result)
            except Exception as e:
                logger.error(f"处理话题 {keyword} 时发生异常: {str(e)}")
                logger.error(f"异常堆栈: {traceback.format_exc()}")
                results.append({
                    'status': 'error',
                    'message': str(e),
                    'keyword': keyword
                })
    
    return results

def save_hot_searches():
    '''
    执行热搜数据采集并保存到本地

    输出:
        - 控制台打印保存结果
    生成文件:
        - weibo_hot_searches.json
        - dynamic_keywords.json
    '''
    try:
        result = get_weibo_hot_search()
        if result['status'] == 'success':
            # 保存原始热搜数据
            save_data(result['data'], 'weibo_hot_searches.json')
            
            # 提取前50名热搜关键词
            top_keywords = [item['title'] for item in result['data']['hot_searches'][:50]]
            save_data({'keywords': top_keywords}, 'dynamic_keywords.json')
            
            logger.info('成功保存实时热搜数据和动态关键词')
            return True
        else:
            logger.error(f'热搜数据获取失败: {result["message"]}')
            return False
    except Exception as e:
        logger.error(f"保存热搜数据时发生异常: {str(e)}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return False

def load_keywords(filename: str) -> List[str]:
    '''
    专用关键词文件加载方法
    
    Args:
        filename: 关键词文件名
        
    Returns:
        有效关键词列表（自动过滤无效条目）
    '''
    try:
        with open(os.path.join('data', filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [kw for kw in data.get('keywords', []) if isinstance(kw, str) and kw.strip()]
    except FileNotFoundError:
        logger.warning(f'关键词文件 {filename} 不存在')
        return []
    except json.JSONDecodeError:
        logger.error(f'关键词文件 {filename} 格式错误')
        return []
    except Exception as e:
        logger.error(f'加载关键词文件异常: {str(e)}')
        return []

if __name__ == '__main__':
    save_hot_searches()
    keywords = load_keywords('dynamic_keywords.json')
    for keyword in keywords:
        result = get_weibo_topic_detail(keyword)
        if result['status'] == 'success':
            save_data(result['data'], f'weibo_{keyword}_data.json')
            logger.info(f'Successfully saved data for {keyword}')
        else:
            logger.error(f'Error processing {keyword}: {result["message"]}')