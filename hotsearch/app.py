from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from weibo_spider import save_hot_searches, get_weibo_hot_search, batch_get_topic_details, load_keywords
from database import Session, HotSearchRecord, TopicDetailRecord
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import time
import logging
import json
import traceback
import os
import random
import re
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def setup_routes():
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/multi-dimension')
    def get_multi_dimension():
        try:
            session = Session()
            latest_records = session.query(TopicDetailRecord).order_by(desc(TopicDetailRecord.timestamp)).limit(10).all()
            
            result = [{
                "keyword": r.keyword,
                "read": r.read_count,
                "discuss": r.discuss_count,
                "interact": r.interact_count,
                "origin": r.origin_count
            } for r in latest_records]
            
            return jsonify({"data": result})
        except Exception as e:
            logger.error(f"多维数据查询失败: {str(e)}")
            return jsonify({"error": "内部服务器错误"}), 500
        finally:
            session.close()

    @app.route('/api/topic-categories')
    def get_topic_categories():
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            session = Session()
            
            categories = session.query(
                TopicDetailRecord.category,
                func.count(TopicDetailRecord.id)
            ).filter(
                TopicDetailRecord.timestamp >= one_hour_ago
            ).group_by(TopicDetailRecord.category).all()
            
            result = [{"name": c[0], "value": c[1]} for c in categories if c[0]]
            return jsonify({"categories": result})
        
        except Exception as e:
            logger.error(f"分类数据查询失败: {str(e)}")
            return jsonify({"error": "内部服务器错误"}), 500
        finally:
            session.close()

    @app.route('/api/hot-searches')
    def get_hot_searches():
        data = load_keywords('weibo_hot_searches.json')
        return jsonify(data)
        
    @app.route('/api/hot-searches/chart')
    def get_hot_searches_chart():
        try:
            # 获取最近3分钟的数据
            three_minutes_ago = datetime.now() - timedelta(minutes=3)
            session = Session()
            
            # 获取最新的热搜数据
            latest_records = session.query(HotSearchRecord)\
                .order_by(desc(HotSearchRecord.timestamp), desc(HotSearchRecord.hot_value))\
                .limit(52)\
                .all()
            latest_records = sorted(latest_records, key=lambda x: x.hot_value, reverse=True)
            latest_records = latest_records[:20]  # 取前20个
            latest_records = latest_records[::-1]  # 反转顺序
            # 转换为前端需要的格式
            chart_data = {
                'keywords': [record.keyword for record in latest_records],
                'hot_values': [record.hot_value for record in latest_records],
                'timestamp': latest_records[0].timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_records else None
            }
            
            return jsonify(chart_data)
        except Exception as e:
            logger.error(f"获取热搜图表数据失败: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()

    @app.route('/api/geo-distribution')
    def get_geo_distribution():
        try:
            with open('china.json', 'r', encoding='utf-8') as f:
                geo_data = json.load(f)
            session = Session()
            one_hour_ago = datetime.now() - timedelta(hours=1)
            results = session.query(
                TopicDetailRecord.location,
                func.count(TopicDetailRecord.id)
            ).filter(
                TopicDetailRecord.timestamp >= one_hour_ago
            ).group_by(TopicDetailRecord.location).all()
            # 简化版城市经纬度表（如需更多城市可扩展）
            city_coords = {
                "北京": [116.4, 39.9],
                "上海": [121.5, 31.2],
                "广州": [113.3, 23.1],
                "深圳": [114.1, 22.6],
                "杭州": [120.2, 30.3],
                "成都": [104.1, 30.6],
                "重庆": [106.5, 29.5],
                "西安": [108.9, 34.3],
                "武汉": [114.3, 30.6],
                "南京": [118.8, 32.0],
                "天津": [117.2, 39.1],
                "苏州": [120.6, 31.3],
                "长沙": [112.9, 28.2],
                "郑州": [113.6, 34.7],
                "青岛": [120.4, 36.1],
                "沈阳": [123.4, 41.8],
                "合肥": [117.2, 31.8],
                "福州": [119.3, 26.1],
                "厦门": [118.1, 24.4],
                "济南": [117.0, 36.7],
                "大连": [121.6, 38.9],
                "宁波": [121.5, 29.9],
                "哈尔滨": [126.5, 45.8],
                "石家庄": [114.5, 38.0],
                "南昌": [115.9, 28.7],
                "昆明": [102.7, 25.0],
                "南宁": [108.3, 22.8],
                "长春": [125.3, 43.9],
                "兰州": [103.8, 36.1],
                "贵阳": [106.7, 26.6],
                "太原": [112.5, 37.8],
                "乌鲁木齐": [87.6, 43.8],
                "呼和浩特": [111.7, 40.8],
                "拉萨": [91.1, 29.6],
                "海口": [110.3, 20.0],
                "香港": [114.2, 22.3],
                "澳门": [113.5, 22.2]
            }
            # 省会城市映射
            province_capital = {
                "广东": "广州", "北京": "北京", "上海": "上海", "浙江": "杭州", "江苏": "南京",
                "四川": "成都", "重庆": "重庆", "陕西": "西安", "湖北": "武汉", "山东": "济南",
                "天津": "天津", "辽宁": "沈阳", "湖南": "长沙", "河南": "郑州", "福建": "福州",
                "江西": "南昌", "云南": "昆明", "广西": "南宁", "吉林": "长春", "甘肃": "兰州",
                "贵州": "贵阳", "山西": "太原", "新疆": "乌鲁木齐", "内蒙古": "呼和浩特", "西藏": "拉萨",
                "海南": "海口", "黑龙江": "哈尔滨", "青海": "西宁", "宁夏": "银川", "香港": "香港", "澳门": "澳门"
            }

            values = []
            max_value = 0
            unmatched_locations = []
            for loc, count in results:
                if not loc:
                    continue  # 跳过空location
                city = None
                loc = loc.strip()
                # 判断是否有空格分隔
                if ' ' in loc:
                    # 以第一个空格为界，前为省份，后为城市
                    province, city_candidate = loc.split(' ', 1)
                    city = city_candidate
                else:
                    # 没有空格，尝试用省份名查找省会
                    province = loc
                    city = province_capital.get(province, None)
                if city and city in city_coords:
                    lng, lat = city_coords[city]
                    values.append({"name": city, "value": count, "lng": lng, "lat": lat})
                    if count > max_value:
                        max_value = count
                else:
                    unmatched_locations.append(loc)
            if unmatched_locations:
                logger.warning(f'未能定位的location: {unmatched_locations}')
            
            return jsonify({
                "geoJSON": geo_data,
                "values": values,
                "maxValue": max_value
            })
        except Exception as e:
            logger.error(f'地理数据加载失败: {str(e)}')
            return jsonify({"error": "地图数据加载失败"}), 500
        finally:
            session.close()

    @app.route('/api/category-trend')
    def get_category_trend():
        try:
            session = Session()
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            # 获取分类占比数据
            category_data = session.query(
                func.strftime('%H:%M', HotSearchRecord.timestamp).label('time'),
                TopicDetailRecord.category,
                func.count(TopicDetailRecord.id)
            ).join(TopicDetailRecord, HotSearchRecord.keyword == TopicDetailRecord.keyword).filter(
                HotSearchRecord.timestamp >= one_hour_ago
            ).group_by('time', 'category').all()

            # 处理为时间序列格式
            result = {}
            for time, category, count in category_data:
                if category not in result:
                    result[category] = []
                result[category].append({'time': time, 'value': count})

            # 取前5大分类
            sorted_categories = sorted(result.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            return jsonify(dict(sorted_categories))

        except Exception as e:
            logger.error(f"获取分类趋势失败: {str(e)}")
            return jsonify({"error": "内部服务器错误"}), 500
        except Exception as e:
            logger.error(f"获取趋势数据失败: {str(e)}")
            return jsonify({"error": "内部服务器错误"}), 500
        finally:
            session.close()

    @app.route('/api/hot-searches/cards')
    def get_hot_searches_cards():
        try:
            session = Session()
            latest_records = session.query(HotSearchRecord)\
                .order_by(desc(HotSearchRecord.timestamp), desc(HotSearchRecord.hot_value))\
                .limit(52)\
                .all()
            latest_records = latest_records[::-1]  # 反转顺序以保持最新的在最前面
            latest_records = latest_records[:20]  # 取前20个
            cards_data = [{
                "keyword": record.keyword,
                "hot_value": record.hot_value,
                "url": f"https://s.weibo.com/weibo?q=%23{record.keyword}%23"
            } for record in latest_records]
            
            return jsonify({"cards": cards_data})
        except Exception as e:
            logger.error(f"获取热搜卡片数据失败: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    @app.route('/api/hot-searches/summaries')
    def get_hot_searches_summaries():
        try:
            session = Session()
            latest_records = session.query(TopicDetailRecord)\
                .order_by(desc(TopicDetailRecord.timestamp))\
                .limit(50)\
                .all()
            
            summaries = [{
                "keyword": record.keyword,
                "summary": record.summary,
                "hot_value": record.read_count
            } for record in latest_records if record.summary]
            
            return jsonify({"summaries": summaries})
        except Exception as e:
            logger.error(f"获取热搜摘要数据失败: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

def collect_topic_details():
    """采集话题详情数据的定时任务"""
    try:
        logger.info("开始采集话题详情数据")
        # 从dynamic_keywords.json读取关键词
        keywords_data = load_keywords('dynamic_keywords.json')
        keywords = keywords_data
        
        if not keywords:
            logger.warning("没有找到待采集的关键词")
            return
            
        # 批量获取话题详情
        results = batch_get_topic_details(keywords)
        
        # 记录采集结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"话题详情采集完成: 成功{success_count}个, 失败{len(keywords)-success_count}个")
        
    except Exception as e:
        logger.error(f"话题详情采集任务异常: {str(e)}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")

# 定时任务保持不变
if __name__ == '__main__':
    setup_routes()
    scheduler = BackgroundScheduler()
    
    # 热搜采集任务（1分钟间隔）
    scheduler.add_job(
        lambda: (save_hot_searches() or logger.info('[Scheduler] 热搜数据存储完成')), 
        'interval', 
        minutes=1, 
        misfire_grace_time=60
    )
    
    # 话题详情采集任务（改为1分钟间隔，方便调试）
    scheduler.add_job(
        collect_topic_details,
        'interval',
        minutes=1,  # 改为1分钟
        misfire_grace_time=60
    )
    
    # 获取并打印任务信息
    jobs = scheduler.get_jobs()
    for job in jobs:
        try:
            next_run = job.next_run_time
            logger.info(f'[Scheduler] 任务 {job.name} 下次执行时间: {next_run}')
        except AttributeError:
            logger.warning(f'[Scheduler] 无法获取任务 {job.name} 的下次运行时间')
    
    scheduler.start()
    app.run(port=5000)