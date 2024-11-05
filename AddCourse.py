from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)
MAX_CREDITS = 25  # 假設學分上限為 25

def parse_time(course_time):
    # 假設時間格式為 "週一 09:00-11:00"
    day, hours = course_time.split()
    start_time, end_time = hours.split("-")
    
    # 將「週幾」轉成數字方便比較
    day_mapping = {"週一": 1, "週二": 2, "週三": 3, "週四": 4, "週五": 5}
    day_num = day_mapping[day]
    
    # 將時間轉成 datetime 格式
    start_time = datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.strptime(end_time, "%H:%M").time()
    
    return day_num, start_time, end_time

def is_conflict(time1, time2):
    # 解析兩個課程的時間
    day1, start1, end1 = parse_time(time1)
    day2, start2, end2 = parse_time(time2)
    
    # 比較是否同一天且時間重疊
    if day1 == day2:
        if (start1 < end2) and (end1 > start2):
            return True
    return False

def add_course(student_id, course_id):
    # 讀取 Excel 檔案的不同 sheet
    data = pd.read_excel("course_data.xlsx", sheet_name=None)
    courses = data['courses']  # 課程資料 sheet
    students = data['students']  # 學生選課資料 sheet

    # 找出學生的選課清單
    student_courses = students[students['student_id'] == student_id]
    new_course = courses[courses['course_id'] == course_id].iloc[0]

    # 檢查衝堂
    for _, course in student_courses.iterrows():
        course_info = courses[courses['course_id'] == course['course_id']].iloc[0]
        if is_conflict(course_info['time'], new_course['time']):
            return "課程衝堂"

    # 檢查學分數
    total_credits = sum(courses[courses['course_id'].isin(student_courses['course_id'])]['credits']) + new_course['credits']
    if total_credits > MAX_CREDITS:
        return "超出學分上限"

    # 檢查人數限制
    if new_course['enrolled'] >= new_course['max_capacity']:
        return "課程已滿"

    # 加選成功，更新學生選課資料
    new_row = {'student_id': student_id, 'course_id': course_id}
    students = pd.concat([students, pd.DataFrame([new_row])], ignore_index=True)
    courses.loc[courses['course_id'] == course_id, 'enrolled'] += 1

    # 儲存更新後的資料
    with pd.ExcelWriter("course_data.xlsx") as writer:
        courses.to_excel(writer, sheet_name="courses", index=False)
        students.to_excel(writer, sheet_name="students", index=False)

    return "加選成功"

@app.route('/add_course', methods=['POST'])
def add_course_route():
    data = request.get_json()  # 獲取 POST 請求的 JSON 資料
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    
    # 執行加選邏輯
    result = add_course(student_id, course_id)
    
    # 返回加選結果
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)
