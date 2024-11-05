from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
MAX_CREDITS = 25  # 假設學分上限為 25

# 重新定義 courses 表的欄位名稱
COURSES_COLUMNS = [
    "day", "time", "course_id", "course_name", "teacher", 
    "location", "extra_info", "grades", "credits", 
    "max_capacity", "enrolled"
]

def parse_time(course_time):
    # 假設時間格式為 "10:10~11:00"
    start_time, end_time = course_time.split("~")
    start_time = datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.strptime(end_time, "%H:%M").time()
    return start_time, end_time

def is_conflict(time1, time2):
    start1, end1 = parse_time(time1)
    start2, end2 = parse_time(time2)
    return (start1 < end2) and (end1 > start2)

def add_course(student_id, course_id):
    # 讀取 Excel 檔案，設置 courses 表的列名
    data = pd.read_excel("course_data.xlsx", sheet_name=None)
    courses = data['courses']
    courses.columns = COURSES_COLUMNS
    students = data['students']

    # 找出學生的選課清單
    student_courses = students[students['student_id'] == student_id]

    # 找出新課程資料
    new_course = courses[courses['course_id'] == course_id]
    if new_course.empty:
        return f"課程 ID '{course_id}' 不存在"

    # 提取新課程的第一筆資料
    new_course = new_course.iloc[0]
   
    # 檢查衝堂
    for _, course in student_courses.iterrows():
        course_info = courses[courses['course_id'] == course['course_id']].iloc[0]
        if course_info["day"] == new_course["day"] and is_conflict(course_info['time'], new_course['time']):
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
    # app.run(debug=True)
    result = add_course('S001','C107')
    print(result)
