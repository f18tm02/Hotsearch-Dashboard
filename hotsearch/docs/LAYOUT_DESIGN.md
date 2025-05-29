# 微博热搜大屏可视化设计方案

## 布局结构
```html
<div class="dashboard-container">
  <!-- 地图模块 -->
  <div class="map-section">
    <div id="chinaMapChart" class="map-card"></div>
  </div>

  <!-- 左栏图表 -->
  <div class="left-panel">
    <div class="chart-card bar-chart">
      <div id="hotSearchChart"></div>
    </div>
    <div class="chart-card donut-chart">
      <div id="categoryChart"></div>
    </div>
    <div class="chart-card line-chart">
      <div id="trendChart"></div>
    </div>
  </div>

  <!-- 右栏榜单 -->
  <div class="right-panel">
    <div class="ranking-card">
      <div class="grid-title">实时热搜榜</div>
      <div id="cardsContainer"></div>
    </div>
  </div>
</div>
```

## 视觉样式规范
```css
/* 基础配色 */
:root {
  --primary-bg: #1a1a1a;
  --secondary-bg: #2d2d2d;
  --accent-blue: #2196F3;
  --accent-cyan: #00BCD4;
  --text-primary: rgba(255,255,255,0.87);
  --text-secondary: rgba(255,255,255,0.6);
}

.dashboard-container {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
  max-width: 3840px;
  padding: 32px;
  background: var(--primary-bg);
}

.map-section {
  grid-column: 1 / -1;
  height: 800px;
  margin-bottom: 32px;
  background: linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%);
  box-shadow: 0 8px 16px rgba(0,0,0,0.3);
  border-radius: 12px;
}

.left-panel {
  display: grid;
  grid-template-rows: repeat(3, 1fr);
  gap: 24px;
}

.chart-card {
  background: var(--secondary-bg);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s ease;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.ranking-card {
  background: var(--secondary-bg);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
```

## 图表配置规范
```javascript
// 统一图表主题配置
echarts.registerTheme('dark-cool', {
  backgroundColor: 'transparent',
  color: ['#2196F3', '#00BCD4', '#4CAF50', '#FFC107', '#9C27B0'],
  textStyle: {
    color: 'rgba(255,255,255,0.87)'
  },
  title: {
    textStyle: {
      color: 'rgba(255,255,255,0.87)',
      fontSize: 24
    },
    subtextStyle: {
      color: 'rgba(255,255,255,0.6)'
    }
  },
  legend: {
    textStyle: {
      color: 'rgba(255,255,255,0.6)'
    }
  },
  tooltip: {
    backgroundColor: '#2d2d2d',
    borderColor: '#2196F3',
    textStyle: {
      color: 'rgba(255,255,255,0.87)'
    }
  }
});

// 初始化图表时应用主题
echarts.init(chartDom, 'dark-cool');
```

## 响应式适配方案
```css
@media (min-width: 2560px) {
  .dashboard-container {
    grid-template-columns: 1.5fr 1fr;
    gap: 48px;
    padding: 64px;
  }
  
  .map-section {
    height: 1000px;
  }
}

@media (max-width: 1920px) {
  .left-panel {
    grid-template-rows: repeat(2, 1fr);
  }
  #trendChart {
    grid-row: 3;
  }
}
```