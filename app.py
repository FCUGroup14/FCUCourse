from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

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
            result = query_result.to_html(index=False, classes="table")  # 使用 to_html 方法生成表格
            return render_template('index.html', result=result)
        else:
            if note == 1:
                return render_template('index.html', error="查無課程代碼")
            if note == 2:
                return render_template('index.html', error="查無{}".format(name))
            if note == 3:
                return render_template('index.html', error="該時段沒有課程")


    return render_template('index.html', result='', error='')

if __name__ == '__main__':
    app.run(debug=True)
