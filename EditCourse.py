from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

class CourseEditor:
    def __init__(self, file_path="course_data.xlsx"):
        self.file_path = file_path
        # 修改為與你的Excel文件完全匹配的列名
        self.COURSES_COLUMNS = [
            'day', 'time', 'course_id', 'course_name', 'teacher',
            'location', 'extra_info', 'grades', 'credits',
            'max_capacity', 'enrolled'
        ]

    def load_data(self):
        """載入Excel數據"""
        try:
            df = pd.read_excel(self.file_path, sheet_name='courses')
            # 確保列名完全匹配
            df.columns = self.COURSES_COLUMNS
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(columns=self.COURSES_COLUMNS)

    def get_all_courses(self):
        """獲取所有課程信息"""
        try:
            df = self.load_data()
            # 直接返回需要顯示的欄位
            courses_list = []
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
                courses_list.append(course)
            return courses_list
        except Exception as e:
            print(f"Error getting courses: {e}")
            return []

    def edit_course(self, course_id, updated_info):
        """編輯課程信息"""
        try:
            df = self.load_data()
            
            # 檢查課程是否存在
            if course_id not in df['course_id'].values:
                return False, "課程不存在"
            
            # 驗證更新的信息
            if 'credits' in updated_info:
                try:
                    credits = float(updated_info['credits'])
                    if credits <= 0:
                        return False, "學分數必須大於0"
                except ValueError:
                    return False, "無效的學分數"
            
            if 'max_capacity' in updated_info:
                try:
                    max_capacity = int(updated_info['max_capacity'])
                    current_enrolled = df.loc[
                        df['course_id'] == course_id, 
                        'enrolled'
                    ].iloc[0]
                    
                    if max_capacity < current_enrolled:
                        return False, "名額不能小於已選修人數"
                except ValueError:
                    return False, "無效的名額數"

            # 更新課程信息
            # 這裡的鍵名已經與Excel完全匹配
            for key, value in updated_info.items():
                if key in self.COURSES_COLUMNS:
                    df.loc[df['course_id'] == course_id, key] = value

            # 保存更新
            df.to_excel(self.file_path, sheet_name='courses', index=False)
            return True, "課程信息更新成功"

        except Exception as e:
            print(f"Error editing course: {e}")
            return False, f"編輯失敗: {str(e)}"

    def delete_course(self, course_id):
        """刪除課程"""
        try:
            df = self.load_data()
            
            # 檢查課程是否存在
            if course_id not in df['course_id'].values:
                return False, "課程不存在"
            
            # 獲取課程信息用於日誌記錄
            course_info = df[df['course_id'] == course_id].iloc[0]
            
            # 刪除課程
            df = df[df['course_id'] != course_id]
            
            # 保存更新
            df.to_excel(self.file_path, sheet_name='courses', index=False)
            return True, f"課程 {course_id} ({course_info['course_name']}) 已成功刪除"

        except Exception as e:
            print(f"Error deleting course: {e}")
            return False, f"刪除失敗: {str(e)}"

# Flask應用
app = Flask(__name__)
course_editor = CourseEditor()

@app.route('/course_management')
def course_management():
    """課程管理頁面路由"""
    courses = course_editor.get_all_courses()
    return render_template('course-management.html', courses=courses)

@app.route('/get_course/<course_id>')
def get_course_route(course_id):
    """獲取特定課程信息的API路由"""
    df = course_editor.load_data()
    course = df[df['course_id'] == course_id].to_dict('records')
    if course:
        return jsonify(course[0])
    return jsonify({"error": "課程不存在"}), 404

@app.route('/edit_course', methods=['POST'])
def edit_course_route():
    """編輯課程的API路由"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "無效的請求數據"}), 400

        course_id = data.get('course_id')
        updated_info = data.get('updated_info')
        
        if not course_id or not updated_info:
            return jsonify({"success": False, "message": "缺少必要參數"}), 400
        
        success, message = course_editor.edit_course(course_id, updated_info)
        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": f"處理請求時發生錯誤: {str(e)}"}), 500

@app.route('/delete_course', methods=['POST'])
def delete_course_route():
    """刪除課程的API路由"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "無效的請求數據"}), 400

        course_id = data.get('course_id')
        if not course_id:
            return jsonify({"success": False, "message": "缺少課程ID"}), 400
        
        success, message = course_editor.delete_course(course_id)
        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": f"處理請求時發生錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)