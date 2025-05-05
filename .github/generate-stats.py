from github import Github
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys

def log_error(message):
    print(f"::error::{message}", file=sys.stderr)
    sys.exit(1)

try:
    # 初始化 GitHub API
    token = os.environ.get('GH_TOKEN')
    if not token:
        log_error("GitHub token not found in environment variables")
    
    g = Github(token)
    
    # 获取当前仓库信息
    repo_name = os.environ.get('GITHUB_REPOSITORY')
    if not repo_name:
        log_error("Repository name not found in environment variables")
    
    repo = g.get_repo(repo_name)
    user = repo.owner

    # 获取所有仓库的提交
    all_commits = []
    try:
        # 首先获取当前仓库的提交
        commits = repo.get_commits(author=user.login)
        for commit in commits:
            all_commits.append(commit)
            
        # 然后获取用户的其他公共仓库的提交
        for repo in user.get_repos():
            if repo.private:
                continue
            try:
                commits = repo.get_commits(author=user.login)
                for commit in commits:
                    all_commits.append(commit)
            except Exception as e:
                print(f"::warning::Error fetching commits from {repo.name}: {str(e)}")
                continue
    except Exception as e:
        log_error(f"Error fetching commits: {str(e)}")

    if not all_commits:
        log_error("No commits found")

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
    def generate_progress_bar(percentage, length=20):
        # 确保百分比在0-100之间
        percentage = max(0, min(100, percentage))
        # 计算填充长度，四舍五入到最接近的整数
        filled = round(percentage * length / 100)
        return '█' * filled + '░' * (length - filled)

    # 读取 README.md
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_error(f"Error reading README.md: {str(e)}")

    # 更新每日提交分布部分
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_section = '<table style="border-collapse: collapse; width: 100%; max-width: 600px; margin: 0 auto; background-color: #161B22;">\n'
    for i, day in enumerate(weekday_names):
        count = weekday_stats[i]
        percentage = weekday_percentages[i]
        progress_bar = generate_progress_bar(percentage)
        weekday_section += f'  <tr>\n'
        weekday_section += f'    <td style="width: 80px; padding: 8px; border: 1px solid #30363d; color: #C9D1D9;">{day}</td>\n'
        weekday_section += f'    <td style="width: 200px; padding: 8px; border: 1px solid #30363d;">{progress_bar}</td>\n'
        weekday_section += f'    <td style="text-align: right; padding: 8px; border: 1px solid #30363d; color: #C9D1D9;">{count} ({percentage:.1f}%)</td>\n'
        weekday_section += f'  </tr>\n'
    weekday_section += '</table>'

    # 更新时间段分布部分
    time_period_names = {
        'morning': 'Morning (6:00-12:00)',
        'afternoon': 'Afternoon (12:00-18:00)',
        'evening': 'Evening (18:00-24:00)',
        'night': 'Night (0:00-6:00)'
    }
    time_period_section = '<table style="border-collapse: collapse; width: 100%; max-width: 600px; margin: 0 auto; background-color: #161B22;">\n'
    for period in ['morning', 'afternoon', 'evening', 'night']:
        count = time_period_stats[period]
        percentage = time_period_percentages[period]
        progress_bar = generate_progress_bar(percentage)
        time_period_section += f'  <tr>\n'
        time_period_section += f'    <td style="width: 120px; padding: 8px; border: 1px solid #30363d; color: #C9D1D9;">{time_period_names[period]}</td>\n'
        time_period_section += f'    <td style="width: 200px; padding: 8px; border: 1px solid #30363d;">{progress_bar}</td>\n'
        time_period_section += f'    <td style="text-align: right; padding: 8px; border: 1px solid #30363d; color: #C9D1D9;">{count} ({percentage:.1f}%)</td>\n'
        time_period_section += f'  </tr>\n'
    time_period_section += '</table>'

    # 替换 README.md 中的相应部分
    content = content.replace(
        '<h4 style="color: #58A6FF;">📊 Daily Commit Distribution</h4>\n<table',
        '<h4 style="color: #58A6FF;">📊 Daily Commit Distribution</h4>\n' + weekday_section
    )
    content = content.replace(
        '<h4 style="color: #58A6FF;">⏰ Time Period Distribution</h4>\n<table',
        '<h4 style="color: #58A6FF;">⏰ Time Period Distribution</h4>\n' + time_period_section
    )

    # 写回 README.md
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        log_error(f"Error writing to README.md: {str(e)}")

    print("::notice::Successfully updated commit statistics")

except Exception as e:
    log_error(f"Unexpected error: {str(e)}") 