import pandas as pd # type: ignore
from openpyxl import load_workbook # type: ignore
import openpyxl

# 讀取excel檔
courseData = load_workbook('courses.xlsx')

print(f'目前使用{courseData.active}')
sheet = courseData.worksheets[:]
print(sheet)

#
Courses = pd.read_excel('courses.xlsx', sheet_name='Courses',usecols="A,B,C,D,I,J,K,L")
print(Courses)
for row in Courses:
	print(row)

# 讀取學生選課資料
student_df = pd.read_excel('courses.xlsx', sheet_name='StudentEnrollments')
# print(student_df)

# def add_course(student_id, course_id):


courseData.save('courses.xlsx')
