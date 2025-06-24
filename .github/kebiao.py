import json
from datetime import datetime, timedelta
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import pytz

# 微信公众号配置
app_id = "wx95dccc37f9d0c4bd"
app_secret = "2c20d3e3d7ae087e5ddeeb4b9c3989ad"
user_ids = "oPSU1vujN9iObbmtzcb9_5NY-vAE"
template_id = "hdmwdmpgA_r8uo6Du8lEXm0baXY-9GRTA161ZKRi5AE"
name = '师靖宇'

# 学期配置
SEMESTER_START = datetime(2025,6,16)  # 学期开始时间

# 课表字符串格式
# 周几|课程名称|教室|开始时间|结束时间|上课周次
courses_str = '''
tuesday|组织行为学|C120316|10:00|11:40|1-6
tuesday|组织行为学|C120316|17:00|14:40|1-6
wednesday|分布式与微服务架构设计|C110301|08:00|11:40|1-6
wednesday|软件测试基础|C120316|13:00|16:40|1-6
thursday|软件测试基础|C120316|08:00|11:40|1-6
thursday|组织行为学|C120316|16:50|18:40|1-6
friday|分布式与微服务架构设计|C110301|08:00|11:40|1-6
'''

def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    utc_now = datetime.utcnow()
    beijing_now = utc_now.replace(tzinfo=pytz.UTC).astimezone(beijing_tz)
    return beijing_now

def is_semester_started():
    """检查学期是否已经开始"""
    now = get_beijing_time()
    return now.replace(tzinfo=None) >= SEMESTER_START

def get_current_week():
    """获取当前教学周"""
    if not is_semester_started():
        return 0
    
    today = get_beijing_time()
    # 计算从学期开始到现在过了多少天
    days_passed = (today.replace(tzinfo=None) - SEMESTER_START).days
    # 计算当前是第几周，开学当周就是第1周
    week = (days_passed // 7) + 1
    
    # 如果是开学当天，直接返回第1周
    if days_passed == 0:
        return 1
        
    return week

def get_upcoming_course():
    """获取即将开始的课程"""
    # 如果学期还没开始，直接返回None
    if not is_semester_started():
        print("学期还未开始")
        return None

    # 获取当前北京时间
    now = get_beijing_time()
    weekday = now.strftime("%A").lower()
    current_week = get_current_week()
    
    if weekday not in courses:
        return None
    
    # 获取当前时间的分钟表示（将小时转换为分钟）
    current_minutes = now.hour * 60 + now.minute
    
    # 遍历当天的所有课程
    for course in courses[weekday]:
        if current_week not in course[4]:  # 如果不在上课周次内，跳过
            continue
            
        # 将课程开始时间转换为分钟表示
        start_hour, start_minute = map(int, course[2].split(":"))
        course_start_minutes = start_hour * 60 + start_minute
        
        # 计算距离上课还有多少分钟
        minutes_until_class = course_start_minutes - current_minutes
        
        # 如果课程在未来15分钟内开始
        if 0 <= minutes_until_class <= 15:
            print(f"找到课程：{course[0]}, 距离上课还有 {minutes_until_class} 分钟")
            return {
                "name": course[0],
                "classroom": course[1],
                "start_time": course[2],
                "end_time": course[3],
                "minutes_until": minutes_until_class
            }
    
    # 打印当前时间和所有课程时间，用于调试
    print(f"当前北京时间：{now.strftime('%H:%M')}")
    print(f"当前分钟数：{current_minutes}")
    print("今日课程：")
    for course in courses[weekday]:
        if current_week in course[4]:
            start_hour, start_minute = map(int, course[2].split(":"))
            course_start_minutes = start_hour * 60 + start_minute
            minutes_until = course_start_minutes - current_minutes
            print(f"- {course[0]}: {course[2]}-{course[3]}, 距离上课还有 {minutes_until} 分钟")
    
    return None

def get_words():
    words = requests.get("https://zj.v.api.aa1.cn/api/wenan-zl/?type=text")
    if words.status_code != 200:
        return get_words()
    text = words.text.strip().replace('<p>', '').replace('</p>', '')
    # 按20个字符分割字符串
    chunk_size = 20
    split_notes = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    [note1, note2, note3, note4, note5] = (split_notes + [""] * 5)[:5]
    return note1, note2, note3, note4, note5

def send_reminder():
    # 如果学期还没开始，打印提示并返回
    if not is_semester_started():
        print(f"学期还未开始，将于 {SEMESTER_START.strftime('%Y年%m月%d日')} 开始")
        return

    # 获取即将开始的课程
    upcoming_course = get_upcoming_course()
    
    # 如果未来15分钟内没有课程，直接返回
    if not upcoming_course:
        print("未来15分钟内没有课程")
        return
    
    try:
        # 如果有课程即将开始，则发送提醒
        client = WeChatClient(app_id, app_secret)
        wm = WeChatMessage(client)
        
        # 获取当前时间
        current_time = get_beijing_time()
        
        # 准备时间字符串
        minutes_str = "马上" if upcoming_course['minutes_until'] == 0 else f"{upcoming_course['minutes_until']}分钟"
        
        # 获取分段温馨寄语
        note1, note2, note3, note4, note5 = get_words()
        data = {
            "first": {
                "value": f"{name}"
            },
            "keyword1": {
                "value": f"今天是{current_time.strftime('%Y年%m月%d日')}第{get_current_week()}周"
            },
            "keyword2": {
                "value": f"{upcoming_course['name']}{upcoming_course['start_time']}上课,还有{minutes_str}"
            },
            "keyword3": {
                "value": f"{upcoming_course['classroom']}"
            },
            "remark1": {
                "value": note1
            },
            "remark2": {
                "value": note2
            },
            "remark3": {
                "value": note3
            },
            "remark4": {
                "value": note4
            },
            "remark5": {
                "value": note5
            }
        }
        
        # 发送消息
        user_id_list = user_ids.split(";")
        for user_id in user_id_list:
            res = wm.send_template(user_id, template_id, data)
            print("发送结果：", res)
    except Exception as e:
        print(f"发送消息时出错：{str(e)}")
        if 'data' in locals():
            print("发送的数据:", data)

def parse_weeks(weeks_str):
    weeks = []
    for part in weeks_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            weeks.extend(range(start, end+1))
        else:
            weeks.append(int(part))
    return weeks

def parse_courses(courses_str):
    courses = {"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": []}
    for line in courses_str.strip().splitlines():
        if not line.strip():
            continue
        weekday, name, classroom, start_time, end_time, weeks_str = line.strip().split('|')
        weeks = parse_weeks(weeks_str)
        courses[weekday.lower()].append([name, classroom, start_time, end_time, weeks])
    return courses

# 自动解析课表
courses = parse_courses(courses_str)

if __name__ == '__main__':
    send_reminder()
