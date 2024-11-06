        # 建立一個空的表格
            table_html = '<table class="table"><tr>' + ''.join([f'<th>{col}</th>' for col in query_result.columns]) + '<th>操作</th></tr>'
            
            # 逐行加入數據
            for _, row in query_result.iterrows():
                # 為每個數據行動態添加 "加選" 按鈕
                table_html += '<tr>' + ''.join([f'<td>{val}</td>' for val in row]) + \
                            f'<td><button onclick="addCourse(\'S001\', \'{row["編號"]}\')">加選</button></td></tr>'
            
            table_html += '</table>'
            
            # 使用渲染的 HTML 表格
            result = table_html
            return render_template('index.html', result=result)