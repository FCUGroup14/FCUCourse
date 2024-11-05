import pandas as pd

# 讀取 Excel 檔案的工作表
df = pd.read_excel('data.xlsx')
#print(df)

while True:
    print("請輸入課程代碼: ")
    print("請輸入課程指導老師名字: ")
    print("請選擇課程時間: ")
    if  number == input("") :
        found = False
        for i in range(len(df)):
            #iloc抓取[行,列]的資料（從0開始）
            data = str(df.iloc[i, 2])
            if data == number:
                found = True
                print(df.iloc[i, :].to_string(index=False))  
        if not found:
            print("課程代碼錯誤")

    if name == input("") :
        

    if time == input("") :
         