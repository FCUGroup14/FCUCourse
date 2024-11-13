from flask import Flask, render_template, request, jsonify, url_for

import pandas as pd
from datetime import datetime
import AddCourse
file_path = "course_data.xlsx"
app = Flask(__name__)
df = pd.read_excel(file_path, sheet_name='courses')
df.columns = ['星期', '時間', '編號', '名稱', '導師', '地點', '介紹', '分數分配', '學分', '總名額', '剩餘名額']

from datetime import datetime

def is_time_contained(selected_time, data_time):
    if '~' not in data_time or '~' not in selected_time:
        return False

    selected_start, selected_end = selected_time.split('~')
    data_start, data_end = data_time.split('~')

    selected_start = datetime.strptime(selected_start.strip(), "%H:%M")
    selected_end = datetime.strptime(selected_end.strip(), "%H:%M")
    data_start = datetime.strptime(data_start.strip(), "%H:%M")
    data_end = datetime.strptime(data_end.strip(), "%H:%M")

    return data_start <= selected_start and data_end >= selected_end




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = request.form['number']
        name = request.form['name']
        time = request.form['time']
        week = request.form['week']
        note = -1

        query_result = df

        if number:
            query_result = query_result[query_result.iloc[:, 2].astype(str) == number]
            note = 1
        if name:
            query_result = query_result[query_result.iloc[:, 4].astype(str) == name]
            note = 2
        if week:
            query_result = query_result[query_result.iloc[:, 0].astype(str) == week]
            note = 3
        if time:
            query_result = query_result[query_result.iloc[:, 1].apply(lambda x: is_time_contained(time, x))]
            note = 3

        if not query_result.empty:
            # 建立一個空的表格
            table_html = '<table class="table"><tr>' + ''.join([f'<th>{col}</th>' for col in query_result.columns]) + '<th>操作</th></tr>'
            
            # 逐行加入數據
            for _, row in query_result.iterrows():
                # 為每個數據行動態添加 "加選" 按鈕
                table_html += '<tr>' + ''.join([f'<td>{val}</td>' for val in row]) + \
                            f'<td><button onclick="add_course(\'S001\', \'{row["編號"]}\')">加選</button></td></tr>'
            
            table_html += '</table>'
            
            # 使用渲染的 HTML 表格
            result = table_html
            return render_template('index.html', result=result)
        else:
            if note == 1:
                return render_template('index.html', error="查無課程代碼")
            if note == 2:
                return render_template('index.html', error="查無{}".format(name))
            if note == 3:
                return render_template('index.html', error="該時段沒有課程")


    return render_template('index.html', result='', error='')
@app.route('/add_course', methods=['POST'])
def add_course_route():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    result = AddCourse.add_course(student_id, course_id)
    
    if "成功" in result:
        redirect_url = url_for('student_schedule', student_id=student_id)
        return jsonify({"redirect": redirect_url})
    else:
        return jsonify({"message": result})
    
time_slots = [
    "08:10~09:00", "09:10~10:00", "10:10~11:00",
    "11:10~12:00", "12:10~13:00", "13:10~14:00",
    "14:10~15:00", "15:10~16:00", "16:10~17:00",
    "17:10~18:00"
]
days_of_week = ["星期一", "星期二", "星期三", "星期四", "星期五"]

def overlaps(time_range1, time_range2):
    """檢查兩個時間範圍是否重疊。"""
    start1, end1 = [datetime.strptime(t, "%H:%M") for t in time_range1.split("~")]
    start2, end2 = [datetime.strptime(t, "%H:%M") for t in time_range2.split("~")]
    return start1 < end2 and end1 > start2

@app.route('/schedule/<student_id>')
def student_schedule(student_id):
    # 重新載入課程資料和學生資料
    df = pd.read_excel(file_path, sheet_name='courses')
    df.columns = ['星期', '時間', '編號', '名稱', '導師', '地點', '介紹', '分數分配', '學分', '總名額', '剩餘名額']
    student_courses_df = pd.read_excel(file_path, sheet_name='students')

    # 選擇學生的課程
    selected_courses = student_courses_df[student_courses_df['student_id'] == student_id]['course_id']

    # 如果學生沒有選課紀錄，顯示空表格
    if selected_courses.empty:
        return render_template('schedule.html', schedule={}, time_slots=time_slots, days_of_week=days_of_week)

    # 過濾出學生選的課程詳細資料
    student_schedule = df[df['編號'].isin(selected_courses)]

    # 初始化課表資料結構
    schedule_data = {day: {time: None for time in time_slots} for day in days_of_week}

    # 將學生的課程填入最相符的或重疊的時間時段
    for _, row in student_schedule.iterrows():
        day = row['星期']
        course_time = row['時間']
        course_info = {'name': row['名稱'], 'location': row['地點']}

        # 找到重疊的所有時段
        matching_slots = [slot for slot in time_slots if overlaps(course_time, slot)]
        
        # 如果有重疊時段，填入課表並設置跨行數
        if day in schedule_data and matching_slots:
            rowspan = len(matching_slots)
            first_slot = matching_slots[0]
            schedule_data[day][first_slot] = {'course_info': course_info, 'rowspan': rowspan}

            # 將其他重疊的時段設置為 None，以便在顯示時略過這些時段
            for slot in matching_slots[1:]:
                schedule_data[day][slot] = None
            print(f"已添加課程 '{course_info['name']}' 至 {day} {first_slot}，跨越 {rowspan} 個時段")
        else:
            print(f"錯誤：無法將課程 '{course_info['name']}' 匹配至預定的時間範圍")

    return render_template('schedule.html', schedule=schedule_data, time_slots=time_slots, days_of_week=days_of_week)
if __name__ == '__main__':
    app.run(debug=True)

# 在現有的 app.py 中添加以下路由

@app.route('/course_management')
def course_management():
    return render_template('course_management.html')

@app.route('/get_courses')
def get_courses():
    try:
        df = pd.read_excel("course_data.xlsx", sheet_name='courses')
        courses = df.to_dict('records')
        return jsonify({"courses": courses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_course/<course_id>')
def get_course(course_id):
    try:
        df = pd.read_excel("course_data.xlsx", sheet_name='courses')
        course = df[df['course_id'] == course_id].to_dict('records')[0]
        return jsonify(course)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
