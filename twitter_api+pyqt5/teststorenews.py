import pandas as pd
import re

def check_news(search,date1,date2):
        
        if  search == '':
            print('No news to find')
            pass

        elif  re.match('[ก-๙]',search) !=  None: #เทียบภาษา หาข่าวไทย
            print('Thai News working')
            data = pd.read_csv('store_thai_news.csv') #ไฟล์ที่เก็บข้อมูล
            data1 = pd.read_csv("keythai_news.csv",names=['date', 'keyword']) #ไฟล์ที่เก็บ search-key แล้วเป็นการกำหนดชื่อ column ให้ตาราง
            search_key = data1['keyword'].unique() #ไม่เอาข้อมูลที่ซ้ำ

            keyword = [] #ไว้ check คำ
            for i in search_key:
                keyword.append(i)
     
            check = []
            colume1 = data1['date'] >= date1
            colume2 = data1['date'] <= date2
            between = data1[colume1 & colume2]
            for i,j in zip(between['date'],between['keyword']):
                op = (i,j)
                check.append(op)
            print(f'Check:{check}')
            
            try :

                if date1 == date2  : #หาแบบ 1 วัน
                    op1 = (date1,search)
                    print(f'Data: {op1}')
                    if op1 in check:
                        print('Store Thai News')
                        c1 = data['Keyword'] == search
                        c2 = data['Date'] == date1
                        check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,าเชื่อมกัน
                        check.to_csv('find_news.csv',index=False)
                        print('done1')

                    elif op1 not in check:
                        print('Find thai-news realtime no date in store')
                   
                    elif search not in keyword: #ไม่เคยหาคำนั้นมาก่อน
                        print('Find news keyword')

                    else : #กรณีอื่นๆ
                        print('find thai news real time')
                                                
                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif date1 != date2 :   #https://www.youtube.com/watch?v=JpKeTfjAqKM
                    op1 = (date1,search)
                    op2 = (date2,search)
                    print(f'Data : {op1},{op2}')
                    if search in keyword and op1 in check or op2 in check:
                        print('Store thai News')
                        df = pd.read_csv('store_thai_news.csv')
                        c1 = data['Keyword'] == search
                        c2 = df['Date'] >= date1
                        c3 = df['Date'] <= date2
                        between1 = df[c1 & c2 & c3]
                        df1 = pd.DataFrame({'keyword':between1['Keyword'],'date':between1['Date'],'Headline':between1['Headline'],'Content':between1['Content'],'Link':between1['Link']})
                        df1.to_csv('find_news.csv',index=False)
                        print('done2')

                    elif op1 not in check or op2 not in check: #เคยหาคำนั้นแต่ไม่มีวัน
                        print('Find thai-news realtime no date in store')

                    elif op1 not in check and op2 not in check :
                        print('Find thai-news realtime no date in store')

                    elif search not in keyword: #ไม่เคยหาคำนั้น
                        print('Find thai-news new-keyword realtime')
                    
                    else : #กรณีอื่นๆ
                        print('find thai-news real time')
                
            except :

                print('Find thai news realtime')
          

        else : #หาข่าวeng

            print('Eng News working')
            data = pd.read_csv('store_eng_news.csv') #ไฟล์ที่เก็บข้อมูล
            data1 = pd.read_csv("keyeng_news.csv",names=['date', 'keyword']) #ไฟล์ที่เก็บ search-key แล้วเป็นการกำหนดชื่อ column ให้ตาราง
            search_key = data1['keyword'].unique() #ไม่เอาข้อมูลที่ซ้ำ
            day_key = data1['date'].unique()

            keyword = [] #ไว้ check คำ
            for i in search_key:
                keyword.append(i)
  
            check = []
            colume1 = data1['date'] >= date1
            colume2 = data1['date'] <= date2
            between = data1[colume1 & colume2] #เก็บช่วงข้อมูลระหว่างตรงนี้โดยเอาข้อมูลทั้งหมดมา
            for i,j in zip(between['date'],between['keyword']):
                op = (i,j)
                check.append(op)
            print(f'Check : {check}')

            try :

                if date1 == date2  : #หาแบบ 1 วัน
                    op1 = (date1,search)
                    print(f'Data :{op1}')
                    if op1 in check:
                        print('Store Eng News')
                        c1 = data['Keyword'] == search
                        c2 = data['Date'] == date1
                        check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,าเชื่อมกัน
                        check.to_csv('find_news.csv',index=False)
                        print('done1')

                    elif op1 not in check:
                        print('Find eng-news realtime no date in store')

                    elif search not in keyword:
                        print('Find eng-news new-keyword realtime')
                    
                    else :
                        print('find eng-news realtime')
                                                                        
                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif date1 != date2 :   #https://www.youtube.com/watch?v=JpKeTfjAqKM
                    op1 = (date1,search)
                    op2 =  (date2,search)
                    print(f'Data :{op1},{op2}')

                    if search in keyword and op1 in check or op2 in check:
                        print('Store Eng News')
                        df = pd.read_csv('store_eng_news.csv')
                        c1 = data['Keyword'] == search
                        c2 = df['Date'] >= date1
                        c3 = df['Date'] <= date2
                        between1 = df[c1 & c2 & c3]
                        df1 = pd.DataFrame({'keyword':between1['Keyword'],'date':between1['Date'],'Headline':between1['Headline'],'Content':between1['Content'],'Link':between1['Link']})
                        df1.to_csv('find_news.csv',index=False)
                        print('done2')
                    
                    elif op1 not in check or op2 not in check :
                        print('Find eng-news realtime no date in store')
                    
                    elif op1 not in check and op2 not in check :
                        print('Find eng-news realtime no date in store')
                    
                    elif search not in keyword:
                        print('Find news new-keyword realtime')

                    else :
                        print('find eng-news real time')

            except :
                print('Find eng-news realtime')

#check_news('กัญชา','25/03/2021','25/03/2021')
#check_news('กัญชา','25/03/2021','29/03/2021')
#check_news('กัญชา','30/03/2021','30/03/2021')
#check_news('ไทย','30/03/2021','30/03/2021')
#check_news('bitcoin','25/03/2021','25/03/2021')
#check_news('bitcoin','25/03/2021','29/03/2021')
#check_news('covid19','30/03/2021','31/03/2021')
check_news('usa','30/03/2021','30/03/2021')
