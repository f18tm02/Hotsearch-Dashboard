// 初始化图表
let chart = echarts.init(document.getElementById('hotSearchChart'));
let lastUpdateTime = document.getElementById('lastUpdateTime');

// 配置项
const option = {
    title: {
        text: '微博热搜实时热度',
        left: 'center'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'value',
        name: '热度值'
    },
    yAxis: {
        type: 'category',
        data: [],
        axisLabel: {
            interval: 0,
            rotate: 30
        }
    },
    series: [{
        name: '热度',
        type: 'bar',
        data: []
    }]
};

// 更新图表数据
function updateChart() {
    // 显示加载动画
    chart.showLoading();
    
    fetch('/api/hot-searches/chart')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('获取数据失败:', data.error);
                return;
            }
            
            // 更新图表数据
            option.yAxis.data = data.keywords;
            option.series[0].data = data.hot_values;
            chart.setOption(option);
            
            // 更新最后更新时间
            const updateTime = new Date(data.timestamp);
            lastUpdateTime.textContent = updateTime.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        })
        .catch(error => {
            console.error('请求失败:', error);
            // 显示错误提示
            chart.hideLoading();
            chart.setOption({
                title: {
                    text: '数据加载失败，请稍后重试',
                    textStyle: {
                        color: '#ff0000'
                    }
                }
            });
        })
        .finally(() => {
            // 隐藏加载动画
            chart.hideLoading();
        });
}

// 初始加载
updateChart();

// 每1分钟自动刷新一次
setInterval(updateChart, 60 * 1000);

// 监听窗口大小变化，调整图表大小
window.addEventListener('resize', () => {
    chart.resize();
}); 