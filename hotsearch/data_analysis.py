'''
微博话题数据分析模块

该模块提供以下核心功能：
1. 数据加载与验证：从JSON文件加载数据并验证数据结构完整性
2. 基础指标提取：阅读量、讨论量等基础传播指标分析
3. 趋势分析：24小时阅读增长、30天阅读总量等趋势数据提取
4. 报告生成：生成包含完整分析指标的CSV格式报告

主要类：
- WeiboDataAnalyzer: 核心分析类，封装完整分析流程
'''
import os
import csv
from datetime import datetime
from utils.data_loader import load_data
import logging

logger = logging.getLogger(__name__)

class WeiboDataAnalyzer:
    def __init__(self, data_or_filename):
        '''
        初始化数据分析实例

        参数:
            data_or_filename (str|dict): 微博话题数据JSON文件路径或数据字典

        异常:
            ValueError: 当数据加载失败时抛出
        '''
        if isinstance(data_or_filename, str):
            self.filename = data_or_filename
            self.data = self._load_data()
        else:
            self.data = data_or_filename
            self._validate_data_structure()

    def _load_data(self):
        try:
            return load_data(self.filename)
        except Exception as e:
            raise ValueError(f"数据加载失败: {str(e)}")

    def _validate_data_structure(self):
        required_fields = [
            'topic_data.baseInfo.count',
            'topic_data.baseInfo.object.category_str'
        ]
        for field in required_fields:
            keys = field.split('.')
            data = self.data
            for key in keys:
                if key in data:
                    data = data[key]

    def extract_basic_metrics(self):
        """
        提取基础传播指标
        """
        try:
            count = self.data['topic_data']['baseInfo']['count']
            return {
                '分类': self.data['topic_data']['baseInfo']['object'].get('category_str', '未知'),
                '摘要': self.data['topic_data']['baseInfo']['object'].get('summary', ''),
                '地域': self.data['topic_data']['baseInfo'].get('claim_info', {}).get('location', '') if isinstance(self.data['topic_data']['baseInfo'].get('claim_info'), dict) else '',
                '阅读量': int(count.get('read', 0)),
                '讨论量': int(count.get('mention', 0)),
                '互动量': int(count.get('interact', 0)),
                '原创量': int(count.get('ori_m', 0))
            }
        except Exception as e:
            logger.error(f"提取基础指标失败: {str(e)}")
            raise

    def extract_trend_data(self):
        """提取趋势数据（防御性编程）"""
        try:
            trend = self.data['topic_data'].get('baseInfo', {})
            return {
                '24小时阅读增长': int(trend.get('24h_read', 0)),
                '30天阅读总量': int(trend.get('30d_read', 0)),
                '最新更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"提取趋势数据失败: {str(e)}")
            raise

    def generate_report(self, output_filename='analysis_report.csv'):
        """生成分析报告（增加目录创建）"""
        os.makedirs('data', exist_ok=True)
        metrics = self.extract_basic_metrics()
        trend = self.extract_trend_data()

        fieldnames = list(metrics.keys()) + list(trend.keys())
        row_data = list(metrics.values()) + list(trend.values())

        with open(f'data/{output_filename}', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            writer.writerow(row_data)


class WeiboHotSearchAnalyzer:
    def __init__(self, filename):
        '''
        初始化热搜数据分析实例

        参数:
            filename (str): 微博热搜数据JSON文件路径

        异常:
            ValueError: 当文件加载失败时抛出

        示例:
            >>> analyzer = WeiboHotSearchAnalyzer('weibo_hot_searches.json')
        '''
        self.filename = filename
        self.data = self._load_hot_data()

    def _load_hot_data(self):
        '''
        加载热搜数据文件

        返回:
            dict: 包含热搜数据的字典

        异常:
            ValueError: 当文件加载失败或数据格式异常时抛出
        '''
        try:
            return load_data(self.filename)
        except Exception as e:
            raise ValueError(f"热搜数据加载失败: {str(e)}")

    def analyze_hot_searches(self):
        '''
        解析热搜条目详细信息

        返回:
            list[dict]: 包含热搜条目字典的列表，每个字典包含:
                - 时间 (str): 热搜时间戳
                - 关键词 (str): 热搜关键词
                - 热度 (int): 实时热度值
                - 排名 (int): 当前排名位置

        示例:
            >>> hot_data = analyzer.analyze_hot_searches()
            >>> print(hot_data[0]['关键词'])
            "热门事件关键词"
        '''
        return [{
            '时间': item['timestamp'],
            '关键词': item['title'],
            '热度': item['hot_value'],
            '排名': item['rank'] + 1
        } for item in self.data['hot_searches']]

    def generate_hot_report(self, output_filename='hot_analysis.csv'):
        '''
        生成热搜详细分析报告

        参数:
            output_filename (str): 输出文件名，默认为hot_analysis.csv

        返回:
            str: 生成文件的绝对路径

        异常:
            IOError: 当文件写入失败时抛出
        '''
        hot_data = self.analyze_hot_searches()
        
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['时间', '关键词', '热度', '排名'])
            writer.writeheader()
            writer.writerows(hot_data)
        return os.path.abspath(output_filename)

if __name__ == '__main__':
    analyzer = WeiboDataAnalyzer('weibo_官方通报潮汕豪宅英之园将强拆_data.json')
    analyzer.generate_report()
    analyzer = WeiboHotSearchAnalyzer('weibo_hot_searches.json')
    analyzer.generate_hot_report()