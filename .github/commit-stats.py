import requests
import os
from datetime import datetime, timedelta
from dateutil import parser
import json
from collections import defaultdict

# 获取环境变量
token = os.environ["GH_TOKEN"]
username = os.environ["GH_USER"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

def get_commits():
    # 获取过去30天的提交
    since = (datetime.now() - timedelta(days=30)).isoformat()
    url = f"https://api.github.com/search/commits?q=author:{username}+committer-date:>{since}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching commits: {response.status_code}")
        return []
    
    commits = response.json()["items"]
    return commits

def calculate_stats(commits):
    # 按星期几统计提交
    weekday_commits = defaultdict(int)
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # 按时间段统计提交
    time_periods = {
        'morning': 0,    # 6:00-12:00
        'afternoon': 0,  # 12:00-18:00
        'evening': 0,    # 18:00-24:00
        'night': 0       # 0:00-6:00
    }
    
    # 按周统计提交
    weekly_commits = defaultdict(int)
    
    for commit in commits:
        date = parser.parse(commit["commit"]["committer"]["date"])
        
        # 统计星期几
        weekday = date.weekday()
        weekday_commits[weekday] += 1
        
        # 统计时间段
        hour = date.hour
        if 6 <= hour < 12:
            time_periods['morning'] += 1
        elif 12 <= hour < 18:
            time_periods['afternoon'] += 1
        elif 18 <= hour < 24:
            time_periods['evening'] += 1
        else:
            time_periods['night'] += 1
        
        # 统计周提交
        week_number = date.isocalendar()[1]
        weekly_commits[week_number] += 1
    
    # 计算总提交数
    total_commits = sum(weekday_commits.values())
    
    # 计算每天的百分比
    weekday_percentages = {}
    for day in range(7):
        count = weekday_commits[day]
        percentage = (count / total_commits * 100) if total_commits > 0 else 0
        weekday_percentages[weekday_names[day]] = percentage
    
    # 计算每日平均提交
    days_with_commits = sum(1 for count in weekday_commits.values() if count > 0)
    daily_average = total_commits / days_with_commits if days_with_commits > 0 else 0
    
    # 找出最活跃的时间段
    most_active_period = max(time_periods.items(), key=lambda x: x[1])[0]
    
    # 计算每周提交趋势
    weeks = sorted(weekly_commits.keys())
    weekly_trend = [weekly_commits[week] for week in weeks]
    
    # 确保至少有3周的数据
    while len(weekly_trend) < 3:
        weekly_trend.insert(0, 0)
    
    return {
        "weekday_commits": weekday_commits,
        "weekday_percentages": weekday_percentages,
        "total_commits": total_commits,
        "daily_average": daily_average,
        "most_active_period": most_active_period,
        "time_periods": time_periods,
        "weekly_trend": weekly_trend[-3:]  # 只返回最近3周的数据
    }

def update_readme(stats):
    # 读取 README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 准备新的统计信息
    stats_section = f"""
## 📈 Commit Statistics

<div align="center">
  <h3>Weekly Commit Distribution</h3>
  
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={username}&theme=github-compact" alt="Activity Graph" />
  
  <p>
    <img src="https://img.shields.io/badge/Total%20Commits-{stats['total_commits']}-orange" alt="Total Commits" />
    <img src="https://img.shields.io/badge/Daily%20Average-{stats['daily_average']:.1f}-blue" alt="Daily Average" />
    <img src="https://img.shields.io/badge/Most%20Active-{stats['most_active_period'].capitalize()}-green" alt="Most Active Time" />
  </p>
  
  <h4>Daily Commit Distribution</h4>
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;">
    <img src="https://img.shields.io/badge/Monday-{stats['weekday_commits'][0]}%20commits%20({stats['weekday_percentages']['Monday']:.1f}%25)-blue" alt="Monday" />
    <img src="https://img.shields.io/badge/Tuesday-{stats['weekday_commits'][1]}%20commits%20({stats['weekday_percentages']['Tuesday']:.1f}%25)-green" alt="Tuesday" />
    <img src="https://img.shields.io/badge/Wednesday-{stats['weekday_commits'][2]}%20commits%20({stats['weekday_percentages']['Wednesday']:.1f}%25)-yellow" alt="Wednesday" />
    <img src="https://img.shields.io/badge/Thursday-{stats['weekday_commits'][3]}%20commits%20({stats['weekday_percentages']['Thursday']:.1f}%25)-red" alt="Thursday" />
    <img src="https://img.shields.io/badge/Friday-{stats['weekday_commits'][4]}%20commits%20({stats['weekday_percentages']['Friday']:.1f}%25)-purple" alt="Friday" />
    <img src="https://img.shields.io/badge/Saturday-{stats['weekday_commits'][5]}%20commits%20({stats['weekday_percentages']['Saturday']:.1f}%25)-orange" alt="Saturday" />
    <img src="https://img.shields.io/badge/Sunday-{stats['weekday_commits'][6]}%20commits%20({stats['weekday_percentages']['Sunday']:.1f}%25)-lightgrey" alt="Sunday" />
  </div>
  
  <h4>Time Period Distribution</h4>
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;">
    <img src="https://img.shields.io/badge/Morning%20(6:00-12:00)-{stats['time_periods']['morning']}%20commits-blue" alt="Morning" />
    <img src="https://img.shields.io/badge/Afternoon%20(12:00-18:00)-{stats['time_periods']['afternoon']}%20commits-green" alt="Afternoon" />
    <img src="https://img.shields.io/badge/Evening%20(18:00-24:00)-{stats['time_periods']['evening']}%20commits-yellow" alt="Evening" />
    <img src="https://img.shields.io/badge/Night%20(0:00-6:00)-{stats['time_periods']['night']}%20commits-red" alt="Night" />
  </div>
  
  <h4>Weekly Trend</h4>
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;">
    <img src="https://img.shields.io/badge/This%20Week-{stats['weekly_trend'][-1]}%20commits-blue" alt="This Week" />
    <img src="https://img.shields.io/badge/Last%20Week-{stats['weekly_trend'][-2]}%20commits-green" alt="Last Week" />
    <img src="https://img.shields.io/badge/Two%20Weeks%20Ago-{stats['weekly_trend'][-3]}%20commits-yellow" alt="Two Weeks Ago" />
  </div>
</div>
"""
    
    # 查找插入位置
    if "## 📈 Commit Statistics" in content:
        # 更新现有统计
        start = content.find("## 📈 Commit Statistics")
        end = content.find("##", start + 1)
        if end == -1:
            end = len(content)
        content = content[:start] + stats_section + content[end:]
    else:
        # 在 GitHub Stats 部分后插入新统计
        stats_pos = content.find("## 📊 GitHub Stats")
        if stats_pos != -1:
            next_section_pos = content.find("##", stats_pos + 1)
            if next_section_pos == -1:
                next_section_pos = len(content)
            content = content[:next_section_pos] + stats_section + content[next_section_pos:]
    
    # 写回 README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    commits = get_commits()
    stats = calculate_stats(commits)
    update_readme(stats)

if __name__ == "__main__":
    main() 