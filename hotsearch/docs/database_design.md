# 微博热搜数据库设计文档

## 1. 热榜数据表结构（hot_searches）
| 字段名 | 类型 | 说明 | 索引 |
|--------|------|------|------|
| id | Integer | 自增主键 | PK |
| timestamp | DateTime | 记录时间（默认当前时间） | 联合索引(timestamp) |
| keyword | String(100) | 热搜关键词 | 全文索引 |
| rank | Integer | 实时排名 | 单列索引 |
| hot_value | Integer | 热度值 | 单列索引 |


## 2. 话题详情表结构（topic_details）
| 字段名 | 类型 | 说明 | 索引 |
|--------|------|------|------|
| id | Integer | 自增主键 | PK |
| timestamp | DateTime | 记录时间 | 时间范围索引 |
| keyword | String(100) | 话题关键词 | 联合索引(keyword,timestamp) |
| read_count | Integer | 阅读量 | 单列索引 |
| discuss_count | Integer | 讨论量 | - |
| interact_count | Integer | 互动量 | - |
| category | string | 分类 | 单列索引 |
| origin_count | Integer | 原创量 | - |
| trend_24h | Integer | 24小时趋势 | 降序索引 |
| trend_30d | Integer | 30天趋势 | 降序索引 |
| summary | string | 分类 | 单列索引 |
| locaton | string | 地域 | 单列索引 |

## 3. 时间序列存储方案
1. **数据分区策略**
   - 按周分表存储（hot_searches_2024w25）
   - 自动归档三个月前的历史数据
   - 建立时序视图统一查询接口

2. **存储优化**
```python
# 自动分表示例
class HotSearchArchive(Base):
    __tablename__ = 'hot_searches_2024w25'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    keyword = Column(String(100))
    rank = Column(Integer)
    hot_value = Column(Integer)
    __table_args__ = {'info': {'partition': '2024w25'}}
```

## 4. 索引设计规范
| 索引名称 | 字段组合 | 索引类型 | 适用场景 |
|----------|----------|----------|----------|
| idx_hotsearch_ts | (timestamp) | 联合索引 | 时间范围查询 |
| idx_topic_kw_ts | (keyword,timestamp) | 覆盖索引 | 话题历史分析 |
| idx_hot_value | (hot_value DESC) | 降序索引 | 热度排行榜单 |
| idx_24h_trend | (trend_24h DESC) | 表达式索引 | 突发趋势检测 |

> 索引使用建议：
> 1. 查询条件包含timestamp字段时必须带上时间范围
> 2. 高频更新字段（rank）采用非聚簇索引
> 3. 文本字段（keyword）使用前缀索引（length=20）