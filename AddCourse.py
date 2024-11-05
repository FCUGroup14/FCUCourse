import pandas as pd

def add_course(student_id, course_id):
    # 讀取 Excel 檔案
    students = pd.read_excel("students.xlsx")
    courses = pd.read_excel("courses.xlsx")

    # 取得學生的已選課程與新課程的詳細資料
    student_courses = students.loc[students['ID'] == student_id, 'courses'].tolist()
    new_course = courses.loc[courses['course_id'] == course_id].iloc[0]

    # 檢查衝堂
    for course in student_courses:
        existing_course = courses.loc[courses['course_id'] == course].iloc[0]
        if is_conflict(existing_course['time'], new_course['time']):
            return "課程衝堂"

    # 檢查學分數
    total_credits = sum(courses.loc[courses['course_id'].isin(student_courses), 'credits']) + new_course['credits']
    if total_credits > MAX_CREDITS:
        return "超出學分上限"

    # 檢查人數限制
    if new_course['enrolled'] >= new_course['max_capacity']:
        return "課程已滿"

    # 加選成功，更新學生選課資料
    student_courses.append(course_id)
    students.loc[students['ID'] == student_id, 'courses'] = student_courses
    courses.loc[courses['course_id'] == course_id, 'enrolled'] += 1

    # 儲存更新後的資料
    students.to_excel("students.xlsx", index=False)
    courses.to_excel("courses.xlsx", index=False)

    return "加選成功"
