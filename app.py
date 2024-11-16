from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
from datetime import datetime
import AddCourse

app = Flask(__name__)
file_path = "course_data.xlsx"

# 統一使用兩種列名映射（管理界面和學生界面）
ADMIN_COLUMNS = [
    "day", "time", "course_id", "course_name", "teacher",
    "location", "extra_info", "grades", "credits",
    "max_capacity", "enrolled"
]

STUDENT_COLUMNS = ['星期', '時間', '編號', '名稱', '導師', '地點', '介紹', 
                  '分數分配', '學分', '總名額', '剩餘名額']

def load_admin_data():
    """載入管理界面數據"""
    try:
        df = pd.read_excel(file_path, sheet_name='courses')
        df.columns = ADMIN_COLUMNS
        return df
    except Exception as e:
        print(f"Error loading admin data: {e}")
        return pd.DataFrame(columns=ADMIN_COLUMNS)

def load_student_data():
    """載入學生界面數據"""
    try:
        df = pd.read_excel(file_path, sheet_name='courses')
        df.columns = STUDENT_COLUMNS
        return df
    except Exception as e:
        print(f"Error loading student data: {e}")
        return pd.DataFrame(columns=STUDENT_COLUMNS)

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

@app.route('/')
def main():
    return render_template('first.html')

@app.route('/student', methods=['GET', 'POST'])
def index():
    df = load_student_data()
    if request.method == 'POST':
        number = request.form['number']
        name = request.form['name']
        time = request.form['time']
        week = request.form['week']
        note = -1

        query_result = df

        if number:
            query_result = query_result[query_result['編號'].astype(str) == number]
            note = 1
        if name:
            query_result = query_result[query_result['導師'].astype(str) == name]
            note = 2
        if week:
            query_result = query_result[query_result['星期'].astype(str) == week]
            note = 3
        if time:
            query_result = query_result[query_result['時間'].apply(lambda x: is_time_contained(time, x))]
            note = 3

        if not query_result.empty:
            table_html = '<table class="table"><tr>' + ''.join([f'<th>{col}</th>' for col in query_result.columns]) + '<th>操作</th></tr>'
            for _, row in query_result.iterrows():
                table_html += '<tr>' + ''.join([f'<td>{val}</td>' for val in row]) + \
                            f'<td><button onclick="add_course(\'S001\', \'{row["編號"]}\')">加選</button></td></tr>'
            table_html += '</table>'
            return render_template('index.html', result=table_html)
        else:
            if note == 1:
                return render_template('index.html', error="查無課程代碼")
            if note == 2:
                return render_template('index.html', error=f"查無{name}")
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

# 課程管理相關路由
@app.route('/course_management')
def course_management():
    try:
        df = load_admin_data()
        courses = []
        for _, row in df.iterrows():
            course = {
                'course_id': row['course_id'],
                'course_name': row['course_name'],
                'teacher': row['teacher'],
                'time': row['time'],
                'location': row['location'],
                'credits': row['credits'],
                'max_capacity': row['max_capacity']
            }
            courses.append(course)
        return render_template('course-management.html', courses=courses)
    except Exception as e:
        print(f"Error in course_management: {e}")
        return render_template('course-management.html', courses=[])

@app.route('/get_course/<course_id>')
def get_course(course_id):
    try:
        df = load_admin_data()
        course = df[df['course_id'] == course_id].to_dict('records')
        if course:
            return jsonify(course[0])
        return jsonify({"error": "課程不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_course', methods=['POST'])
def edit_course():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "無效的請求數據"}), 400

        course_id = data.get('course_id')
        updated_info = data.get('updated_info')
        
        if not course_id or not updated_info:
            return jsonify({"success": False, "message": "缺少必要參數"}), 400
            
        df = load_admin_data()
        
        if course_id not in df['course_id'].values:
            return jsonify({"success": False, "message": "課程不存在"}), 404
            
        for key, value in updated_info.items():
            if key in ADMIN_COLUMNS:
                df.loc[df['course_id'] == course_id, key] = value
                
        df.to_excel(file_path, sheet_name='courses', index=False)
        return jsonify({"success": True, "message": "課程信息更新成功"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"更新失敗: {str(e)}"}), 500

@app.route('/delete_course', methods=['POST'])
def delete_course():
    try:
        data = request.get_json()
        if not data or 'course_id' not in data:
            return jsonify({"success": False, "message": "缺少課程ID"}), 400
            
        course_id = data['course_id']
        df = load_admin_data()
        
        if course_id not in df['course_id'].values:
            return jsonify({"success": False, "message": "課程不存在"}), 404
            
        course_info = df[df['course_id'] == course_id].iloc[0]
        df = df[df['course_id'] != course_id]
        df.to_excel(file_path, sheet_name='courses', index=False)
        
        return jsonify({
            "success": True, 
            "message": f"課程 {course_id} ({course_info['course_name']}) 已成功刪除"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"刪除失敗: {str(e)}"}), 500

@app.route('/schedule/<student_id>')
def student_schedule(student_id):
    df = load_student_data()
    student_courses_df = pd.read_excel(file_path, sheet_name='students')

    selected_courses = student_courses_df[student_courses_df['student_id'] == student_id]['course_id']

    if selected_courses.empty:
        return render_template('schedule.html', schedule={}, time_slots=time_slots, days_of_week=days_of_week)

    student_schedule = df[df['編號'].isin(selected_courses)]
    schedule_data = {day: {time: None for time in time_slots} for day in days_of_week}

    for _, row in student_schedule.iterrows():
        day = row['星期']
        course_time = row['時間']
        course_info = {'name': row['名稱'], 'location': row['地點']}
        
        matching_slots = [slot for slot in time_slots if overlaps(course_time, slot)]
        
        if day in schedule_data and matching_slots:
            rowspan = len(matching_slots)
            first_slot = matching_slots[0]
            schedule_data[day][first_slot] = {'course_info': course_info, 'rowspan': rowspan}
            
            for slot in matching_slots[1:]:
                schedule_data[day][slot] = None

    return render_template('schedule.html', schedule=schedule_data, time_slots=time_slots, days_of_week=days_of_week)

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

if __name__ == '__main__':
    app.run(debug=True)