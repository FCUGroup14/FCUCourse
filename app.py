from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

# 創建 Flask 應用程序
app = Flask(__name__)
# 讀取 Excel 檔案
df = pd.read_excel("course_data.xlsx", sheet_name='courses')
df.columns = ['星期', '時間', '編號', '名稱', '導師', '地點', '介紹', '分數分配', '學分', '總名額', '剩餘名額']

from datetime import datetime

# 改進後的時間包含檢查函數
def is_time_contained(selected_time, data_time):
    # 確保資料時間格式正確
    if '~' not in data_time or '~' not in selected_time:
        return False  # 如果格式不正確，則不包含

    # 解析時間範圍
    selected_start, selected_end = selected_time.split('~')
    data_start, data_end = data_time.split('~')

    # 確保時間格式一致，並轉換為 datetime 對象
    selected_start = datetime.strptime(selected_start.strip(), "%H:%M")
    selected_end = datetime.strptime(selected_end.strip(), "%H:%M")
    data_start = datetime.strptime(data_start.strip(), "%H:%M")
    data_end = datetime.strptime(data_end.strip(), "%H:%M")

    # 檢查資料時間段是否包含用戶選擇的時間段
    return data_start <= selected_start and data_end >= selected_end




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 獲取用戶輸入的資料
        number = request.form['number']
        name = request.form['name']
        time = request.form['time']
        week = request.form['week']
        note = -1

        # 初始化查詢結果為整個資料集
        query_result = df

        # 根據非空的輸入條件進行篩選
        if number:
            query_result = query_result[query_result.iloc[:, 2].astype(str) == number]
            note = 0
        if name:
            query_result = query_result[query_result.iloc[:, 4].astype(str) == name]
            note = 0
        if week:
            query_result = query_result[query_result.iloc[:, 0].astype(str) == week]
            note = 0
        if time:
            query_result = query_result[query_result.iloc[:, 1].apply(lambda x: is_time_contained(time, x))]
            note = 0

        # 檢查篩選後的結果是否為空
        if not query_result.empty:
            result = query_result.to_html(index=False, classes="table")  # 使用 to_html 方法生成表格
            return render_template('index.html', result=result)
        else:
            return render_template('index.html', error="查無符合的資料，請再試一次。")

    return render_template('index.html', result='', error='')

if __name__ == '__main__':
    app.run(debug=True)
