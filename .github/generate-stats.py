from github import Github
from datetime import datetime, timedelta
from collections import defaultdict
import os

# 初始化 GitHub API
g = Github(os.environ['GH_TOKEN'])
user = g.get_user()

# 获取所有仓库的提交
all_commits = []
for repo in user.get_repos():
    try:
        commits = repo.get_commits(author=user.login)
        for commit in commits:
            all_commits.append(commit)
    except:
        continue

# 按星期几统计
weekday_stats = defaultdict(int)
for commit in all_commits:
    weekday = commit.commit.author.date.weekday()
    weekday_stats[weekday] += 1

# 按时间段统计
time_period_stats = defaultdict(int)
for commit in all_commits:
    hour = commit.commit.author.date.hour
    if 6 <= hour < 12:
        time_period_stats['morning'] += 1
    elif 12 <= hour < 18:
        time_period_stats['afternoon'] += 1
    elif 18 <= hour < 24:
        time_period_stats['evening'] += 1
    else:
        time_period_stats['night'] += 1

# 计算总数和百分比
total_commits = len(all_commits)
weekday_percentages = {k: (v/total_commits*100) for k, v in weekday_stats.items()}
time_period_percentages = {k: (v/total_commits*100) for k, v in time_period_stats.items()}

# 生成进度条
def generate_progress_bar(percentage, length=30):
    filled = int(percentage * length / 100)
    return '█' * filled + '░' * (length - filled)

# 读取 README.md
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新每日提交分布部分
weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_section = '<pre>\n'
for i, day in enumerate(weekday_names):
    count = weekday_stats[i]
    percentage = weekday_percentages[i]
    progress_bar = generate_progress_bar(percentage)
    weekday_section += f'{day:<12} {progress_bar} {count:>2} ({percentage:>5.1f}%)\n'
weekday_section += '</pre>'

# 更新时间段分布部分
time_period_names = {
    'morning': 'Morning (6:00-12:00)',
    'afternoon': 'Afternoon (12:00-18:00)',
    'evening': 'Evening (18:00-24:00)',
    'night': 'Night (0:00-6:00)'
}
time_period_section = '<pre>\n'
for period in ['morning', 'afternoon', 'evening', 'night']:
    count = time_period_stats[period]
    percentage = time_period_percentages[period]
    progress_bar = generate_progress_bar(percentage)
    time_period_section += f'{time_period_names[period]:<20} {progress_bar} {count:>2} ({percentage:>5.1f}%)\n'
time_period_section += '</pre>'

# 替换 README.md 中的相应部分
content = content.replace(
    '<h4>Daily Commit Distribution</h4>\n<pre>',
    '<h4>Daily Commit Distribution</h4>\n' + weekday_section
)
content = content.replace(
    '<h4>Time Period Distribution</h4>\n<pre>',
    '<h4>Time Period Distribution</h4>\n' + time_period_section
)

# 写回 README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content) 