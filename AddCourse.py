import pandas as pd

# 讀取課程資料
course_df = pd.read_excel('courses.xlsx', sheet_name='Courses')

# 讀取學生選課資料
student_df = pd.read_excel('courses.xlsx', sheet_name='StudentEnrollments')

def add_course(student_id, course_id):
    # 檢查課程是否已存在，若不存在則加入
    if not ((student_df['student_id'] == student_id) & (student_df['course_id'] == course_id)).any():
        new_enrollment = {'student_id': student_id, 'course_id': course_id}
        student_df.append(new_enrollment, ignore_index=True)
    else:
        print("學生已選修該課程")

# 範例：加選學生 123 的課程 'CS101'
add_course(123, 'CS101')

# 將結果存回 Excel
with pd.ExcelWriter('courses.xlsx', engine='openpyxl', mode='a') as writer:
    student_df.to_excel(writer, sheet_name='StudentEnrollments', index=False)
