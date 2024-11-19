from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
COURSES_COLUMNS = [
    "day", "time", "course_id", "course_name", "teacher", 
    "location", "extra_info", "grades", "credits", 
    "max_capacity", "enrolled"
]
app = Flask(__name__)
MAX_CREDITS = 25  # 假設學分上限為 25

def parse_time(course_time):
    # 假設時間格式為 "10:10~11:00"
    try:
        start_time, end_time = course_time.split("~")
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(end_time, "%H:%M").time()
        return start_time, end_time
    except ValueError:
        return None, None

def is_conflict(time1, time2):
    start1, end1 = parse_time(time1)
    start2, end2 = parse_time(time2)
    if None in [start1, end1, start2, end2]:
        print(f"時間解析錯誤: {time1}, {time2}")
        return False  # 如果有解析錯誤，默認為無衝突
    print(f"比較時間: {start1}-{end1} 與 {start2}-{end2}")
    return (start1 < end2) and (end1 > start2)

def add_course(student_id, course_id):
    try:
        # 載入資料
        courses = pd.read_excel('course_data.xlsx', sheet_name='courses')
        students = pd.read_excel('course_data.xlsx', sheet_name='students')
        courses.columns = COURSES_COLUMNS

        # 找出學生的選課清單
        student_courses = students[students['student_id'] == student_id]
        print("學生已選課程:", student_courses)

        # 找出新課程資料
        new_course = courses[courses['course_id'] == course_id].reset_index(drop=True)
        print("新課程資料:", new_course)
        if new_course.empty:
            return f"課程 ID '{course_id}' 不存在"
        

        # 獲取課程資訊
        new_course = new_course.iloc[0]
        print(new_course)

        # 檢查學生是否已選修該課程
        if not students[(students['student_id'] == student_id) & (students['course_id'] == course_id)].empty:
            return False, f"課程衝堂"


        for _, course in student_courses.iterrows():
            matching_courses = courses[courses['course_id'] == course['course_id']]
            print(f"檢查課程 ID: {course['course_id']}，匹配結果數量: {len(matching_courses)}")
            if matching_courses.empty:
                print(f"找不到課程 ID: {course['course_id']}，請檢查資料是否完整")
                continue
            course_info = matching_courses.iloc[0]


        #print("開始執行衝堂檢查")
        # 衝堂檢查
        #for _, course in student_courses.iterrows():
        #    course_info = courses[courses['course_id'] == course['course_id']].iloc[0]
        #    print(f"檢查課程 {course_info['course_id']} | Day: {course_info['day']} | Time: {course_info['time']}")
        #    print(f"新課程 {new_course['course_id']} | Day: {new_course['day']} | Time: {new_course['time']}")
        #    if course_info["day"] == new_course["day"]:
        #        print("同一天的課程，進行時間檢查...")
        #        if is_conflict(course_info['time'], new_course['time']):
        #            print("衝堂檢查: 發現衝堂")
        #            return False, "課程衝堂"
        #    else:
         #       print("不同天的課程，無需檢查")

        #print("學分檢查開始")
        # 學分檢查
        total_credits = sum(courses[courses['course_id'].isin(student_courses['course_id'])]['credits']) + new_course['credits']
        print(f"目前學分: {total_credits}")
        if total_credits > MAX_CREDITS:
            print("學分超過上限")
            return False, "超出學分上限"

        #print("人數限制檢查開始")
        # 人數限制檢查
        if new_course['enrolled'] == 0:
            print("課程已滿")
            return False, "課程已滿"


        # 新增選課資料
        new_entry = {'student_id': student_id, 'course_id': course_id}
        students = pd.concat([students, pd.DataFrame([new_entry])], ignore_index=True)

        # 排序學生選課資料（假設依 course_id 排序）
        students = students.sort_values(by=['student_id', 'course_id']).reset_index(drop=True)
        courses.loc[courses['course_id'] == course_id, 'enrolled'] -= 1

        # 保存更新後的資料
        with pd.ExcelWriter('course_data.xlsx', engine='openpyxl') as writer:
            courses.to_excel(writer, sheet_name='courses', index=False)
            students.to_excel(writer, sheet_name='students', index=False)

        return True, f"學生 {student_id} 成功新增課程 {course_id} ({course_info['course_name']})。"

    except Exception as e:
        print("錯誤發生:", str(e))  # 增加詳細錯誤輸出
        return False, f"處理過程中發生錯誤：{str(e)}"
