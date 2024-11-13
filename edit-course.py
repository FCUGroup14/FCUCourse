from flask import Flask, request, jsonify
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class CourseEditor:
    def __init__(self, file_path="course_data.xlsx"):
        self.file_path = file_path
        self.COURSES_COLUMNS = [
            "day", "time", "course_id", "course_name", "teacher", 
            "location", "extra_info", "grades", "credits", 
            "max_capacity", "enrolled"
        ]

    def edit_course(self, course_id, updated_info):
        """
        編輯課程資訊
        
        Args:
            course_id (str): 課程ID
            updated_info (dict): 更新的課程資訊
            
        Returns:
            str: 編輯結果訊息
        """
        try:
            # 讀取Excel檔案
            data = pd.read_excel(self.file_path, sheet_name=None)
            courses = data['courses']
            courses.columns = self.COURSES_COLUMNS
            
            # 檢查課程是否存在
            if course_id not in courses['course_id'].values:
                return "課程不存在"
            
            # 更新課程資訊
            for key, value in updated_info.items():
                if key in self.COURSES_COLUMNS:
                    courses.loc[courses['course_id'] == course_id, key] = value
            
            # 儲存更新後的資料
            with pd.ExcelWriter(self.file_path) as writer:
                courses.to_excel(writer, sheet_name="courses", index=False)
                if 'students' in data:
                    data['students'].to_excel(writer, sheet_name="students", index=False)
            
            return "課程資訊更新成功"
            
        except Exception as e:
            return f"編輯失敗: {str(e)}"

    def delete_course(self, course_id):
        """
        刪除課程
        
        Args:
            course_id (str): 課程ID
            
        Returns:
            str: 刪除結果訊息
        """
        try:
            # 讀取Excel檔案
            data = pd.read_excel(self.file_path, sheet_name=None)
            courses = data['courses']
            courses.columns = self.COURSES_COLUMNS
            students = data['students']
            
            # 檢查課程是否存在
            if course_id not in courses['course_id'].values:
                return "課程不存在"
            
            # 取得課程學分數，用於更新學生總學分
            course_credits = courses.loc[courses['course_id'] == course_id, 'credits'].iloc[0]
            
            # 找出選修該課程的學生
            affected_students = students[students['course_id'] == course_id]
            
            # 刪除課程
            courses = courses[courses['course_id'] != course_id]
            
            # 刪除學生選課記錄
            students = students[students['course_id'] != course_id]
            
            # 儲存更新後的資料
            with pd.ExcelWriter(self.file_path) as writer:
                courses.to_excel(writer, sheet_name="courses", index=False)
                students.to_excel(writer, sheet_name="students", index=False)
            
            return f"課程刪除成功，影響 {len(affected_students)} 位學生"
            
        except Exception as e:
            return f"刪除失敗: {str(e)}"

# Flask路由處理
app = Flask(__name__)
course_editor = CourseEditor()

@app.route('/edit_course', methods=['POST'])
def edit_course_route():
    data = request.get_json()
    course_id = data.get('course_id')
    updated_info = data.get('updated_info')
    
    if not course_id or not updated_info:
        return jsonify({"message": "缺少必要參數"}), 400
        
    result = course_editor.edit_course(course_id, updated_info)
    return jsonify({"message": result})

@app.route('/delete_course', methods=['POST'])
def delete_course_route():
    data = request.get_json()
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({"message": "缺少課程ID"}), 400
        
    result = course_editor.delete_course(course_id)
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)
