from flask import Flask, render_template, request, jsonify, url_for

import pandas as pd
from datetime import datetime
import AddCourse
app = Flask(__name__)
df = pd.read_excel("course_data.xlsx", sheet_name='courses')
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

    # 確認成功時包含 "成功" 字樣
    if "成功" in result:
        redirect_url = url_for('student_schedule', student_id=student_id)
        return jsonify({"redirect": redirect_url})
    else:
        return jsonify({"message": result})


# 讀取課程表
df = pd.read_excel("course_data.xlsx", sheet_name='courses')
df.columns = ['星期', '時間', '編號', '名稱', '導師', '地點', '介紹', '分數分配', '學分', '總名額', '剩餘名額']

time_slots = [
    "08:00~09:00", "09:00~10:00", "10:00~11:00",
    "11:00~12:00", "12:00~01:00", "13:10~15:00",
    "14:10~17:00", "15:10~17:00","17:10~18:00"
]
days_of_week = ["星期一", "星期二", "星期三", "星期四", "星期五"]

@app.route('/schedule/<student_id>')
def student_schedule(student_id):
    # 讀取學生選課資料
    student_courses_df = pd.read_excel("course_data.xlsx", sheet_name='students')
    print("學生選課資料：", student_courses_df.head())  # 確認選課資料是否正確

    # 選擇該學生的課程
    selected_courses = student_courses_df[student_courses_df['student_id'] == student_id]['course_id']
    print(f"學生 {student_id} 的選課編號：", selected_courses.tolist())  # 確認該學生的課程編號列表

    # 如果學生沒有選課，顯示空表格
    if selected_courses.empty:
        print(f"學生 {student_id} 沒有選課紀錄。")
        return render_template('schedule.html', schedule={}, time_slots=time_slots, days_of_week=days_of_week)

    # 過濾出學生選的課程詳細資料
    student_schedule = df[df['編號'].isin(selected_courses)]
    print("學生課程詳細資料：\n", student_schedule)  # 確認學生課程詳細資料是否正確

    # 構建課表數據結構
    schedule_data = {day: {time: None for time in time_slots} for day in days_of_week}

    # 將學生的課程填入課表中
    for _, row in student_schedule.iterrows():
        day = row['星期']
        time = row['時間']
        course_info = {
            'name': row['名稱'],
            'location': row['地點']
        }
        # 確認日期和時間是否在預期範圍內
        if day not in schedule_data:
            print(f"錯誤：{day} 不在預期的星期範圍內")
        elif time not in schedule_data[day]:
            print(f"錯誤：{time} 不在預期的時間範圍內")
        else:
            schedule_data[day][time] = course_info
            print(f"已添加課程 '{course_info['name']}' 至 {day} {time}")

    print("最終課表數據：", schedule_data)  # 檢查最終的課表結構

    return render_template('schedule.html', schedule=schedule_data, time_slots=time_slots, days_of_week=days_of_week)

if __name__ == '__main__':
    app.run(debug=True)
