# mini project : 6201012620139
#ref :https://www.youtube.com/watch?v=HDjc3w1W9oA
#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
#search realtime & store
# nlp thai & english
# sentiment + 5 top word + wordcloud + store & update data +select time to show old data
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget,QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from datetime import date
import time
import csv 
import sys
import os
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis
from wordcloud import WordCloud #ใช้แสดงผลกลุ่มคำที่เจอบ่อย
import re #ลบ pattern ของคำที่ไม่ต้องการออกด้วย
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import emoji #ใช้ตอนลบ อีโมจิ
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


form_class = uic.loadUiType("gui.ui")[0]  #dowload gui.ui มาใช้ได้เลย

class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)


        self.lineEdit.setPlaceholderText('Enter your search word')
        self.lineEdit_2.setPlaceholderText('How many tweet to analyze ')

        #connect กับ ปุ่ม
        self.btnsearch.clicked.connect(self.twit) #search
        self.btnopen.clicked.connect(self.OpenFile) #open csv
        self.btnshow.clicked.connect(self.dataHead) #show csv
        self.btnsearch2.clicked.connect(self.find_store) #store data


        #แสดงเทรนทวิต
        self.thai_trendy()
        self.world_trendy()

        #store
        self.str_day()
        self.str_kw()

        self.show()
       
    def twit(self):
        start = time.time()
        #Getting authorization
        self.consumer_key = 
        self.consumer_secret = 
        self.access_token = 
        self.access_token_secret = 
        
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

        self.keyword = self.lineEdit.text()

        self.max_tweet = int(self.lineEdit_2.text())

        self.search_tweet1 = [status for status in tweepy.Cursor(self.api.search, q=self.keyword).items(self.max_tweet)]
        #ตั้งค่าให้รับข้อมูลล่าสุดของทวิตและรับข้อความแบบไม่มีการตัด
        self.search_tweet2 = tweepy.Cursor(self.api.search,q=self.keyword,result_type='recent',tweet_mode='extended').items(self.max_tweet)
        self.search_tweet3 = [status for status in tweepy.Cursor(self.api.search, q=self.keyword).items(1)]
        
        #บันทึกไฟล์ keyword ไว้ check ว่าวันนี้ค้นหาคำว่าอะไรไปบ้าง
        self.data = pd.DataFrame(columns = ['Date','Keyword'])

        for twit in self.search_tweet3:
            if self.keyword != ' ' :
                    key = self.keyword
                    today = date.today()
                    d = today.strftime("%d/%m/%Y")
                    self.add_c = pd.Series([d,key], index=self.data.columns)
                    self.data = self.data.append(self.add_c,ignore_index=True)

        self.data.to_csv('keyword.csv', mode = 'a',header = False , encoding='utf-8',index= False)

        # real time
        self.df = pd.DataFrame(columns= ['keyword','create_at', 'text', 'hashtag', 'retweet_count', 'favourite_count']) 
        #store
        self.df2 = pd.DataFrame(columns= ['keyword','date', 'text', 'hashtag', 'retweet_count', 'favourite_count']) 
        for tweet in self.search_tweet2 :
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ' '
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'# '+entity_hashtag[i]['text']

            create_at = tweet.created_at #เวลา
            re_count = tweet.retweet_count #จน รีทวิต
            keyword = self.keyword
            today = date.today()
            d1 = today.strftime("%d/%m/%Y") #เวลาปจบ

            #หากเจอข้อความในหัวข้อ retweet ให้ใช้ข้อความและจำนวนผู้กด Favourite จากทวิตดั่งเดิม แต่หากไม่พบให้ดึงข้อมูลจากทวิตอันนั้นได้เลย
            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            #all data
            self.new_column = pd.Series([keyword,create_at,text,hashtag,re_count,fav_count], index=self.df.columns)
            self.df = self.df.append(self.new_column,ignore_index=True)
            self.df.sort_values(by=['retweet_count','favourite_count'], inplace=True,ascending=False) #เรียงจากมาก-->น้อย

            #store data
            self.new_column2 = pd.Series([keyword,d1,text,hashtag,re_count,fav_count], index=self.df2.columns)
            self.df2 = self.df2.append(self.new_column2,ignore_index=True)
            self.df2.sort_values(by=['retweet_count','favourite_count'], inplace=True,ascending=False)
        

        print('Search Successful')
        print('-------------------------------------------------------------------------------')
        self.df.to_csv('twitter.csv')  #แปลงเป็น csv ไฟล์
        self.df2.to_csv('store.csv', mode = 'a',header= ['keyword','date','text','hashtag','rt','fav'] , encoding='utf-8',index= True) # ไฟล์ store data เพิ่มข้อมูลต่อท้ายในไฟล์ csv 


        #show top 10 data
        data1 = self.df.drop_duplicates("text").sort_values(by=['retweet_count'], ascending=False).head(10)[['text','retweet_count']]
        data1.to_csv('top10.csv',index= True)

        #analysis
        self.hash_tag('twitter.csv')
        self.emotion('twitter.csv')
        self.word_c('twitter.csv')

        end = time.time()
        t = end-start #จับเวลารัน
        self.runtime.setText("Run : " + str(t)) 

    def emotion(self,path):
        #sentiment
        df = pd.read_csv(path)
        pos = 0
        neg = 0
        neu = 0
        for tweet in df['text']:
            analysis = TextBlob(tweet)
            if analysis.sentiment[0]>0:  #1 is positive
                    pos +=  1
            elif analysis.sentiment[0]<0: #-1 is a negative
                    neg +=  1
            else:   # 0 is independent  
                    neu +=  1

        se = QPieSeries()
        se.append('Positive',pos)
        se.append('Negative',neg)
        se.append('Neutral',neu)

        chart = QChart()
        chart.addSeries(se)
        chart.setTitle('Sentiment')

        chartview = QChartView(chart)
        chartview.setGeometry(0,0,521,421)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.saveapi = QPixmap(chartview.grab())
        self.saveapi.save('C:/software/software2/pic/sent.png','PNG')
        self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent.png);')
    
    def word_c(self,path):
        #word cloud
        word =[]
        df = pd.read_csv(path)
        t = df['text'] #ข้อความทวิตในตาราง

        for item in t :

            if re.match('[ก-๙]',item) !=  None:

                for txt in df["text"]:
                    word.append(self.clean_thai(txt))

            else :

               for txt in df["text"]:
                    word.append(self.clean_eng(txt))
                             
        #wordcloud
        all_words = ' '.join([text for text in word])
        regexp = r"[ก-๙a-zA-Z']+"
        path = 'C:\software\software2\THSarabunNew.ttf'
        wordcloud = WordCloud(font_path=path,background_color="white",max_words=200,width=1100, height=800, random_state=21, max_font_size=150,regexp=regexp).generate(all_words)
        plt.figure(figsize=(16, 12))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis('off')
        plt.savefig('C:/software/software2/pic/word.jpg')
        self.word.setStyleSheet('border-image: url(C:/software/software2/pic/word.jpg);')

    def hash_tag(self,path):
        df = pd.read_csv(path)
        hastag_data = df["hashtag"].dropna() #ลบข้อมูลที่ว่างออก
        vectorizer = CountVectorizer(tokenizer=self.slash_tokenize)#สอนให้เป็นตัวตัดคำ (tokenizer)
        #เพื่อสอน vectorizer ว่ามีคำอะไรบ้างใน data และแปลงข้อมูล data ให้อยู่ในรูปแบบเดียวกับเราสอนให้ vectorizer
        transformed_data = vectorizer.fit_transform(hastag_data)
        hash_tag_cnt_df= pd.DataFrame(columns = ['word', 'count']) #เก็บข้อมูลลง df
        hash_tag_cnt_df['word'] = vectorizer.get_feature_names() # เพื่อให้ได้ข้อมูลคำทั้งหมดที่สอน vectorizer ไป 
        hash_tag_cnt_df['count'] = np.ravel(transformed_data.sum(axis=0))#นับจำนวนคำที่แปลงแล้ว
        data2 = hash_tag_cnt_df.sort_values(by=['count'], ascending=False).head(6)
        data2.to_csv('hashtag.csv',index = True)
        df1 = pd.read_csv('hashtag.csv')
        df2 = df1[1:]

        se = QPieSeries()
        for w,num in zip(df2['word'],df2['count']):
            se.append(w,int(num))

        chart = QChart()
        chart.addSeries(se)
        chart.setTitle('5 top hashtag')

        chartview = QChartView(chart)
        chartview.setGeometry(0,0,560,470)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.saveapi = QPixmap(chartview.grab())
        self.saveapi.save('C:/software/software2/pic/top.png','PNG')
        self.topw.setStyleSheet('border-image: url(C:/software/software2/pic/top.png);')

                
    def slash_tokenize(self,text):  
        self.result = text.split("#") #เพื่อแยกคำด้วย  ' # '
        self.result = list(filter(None, self.result))
        return self.result
   
    def clean_thai(self,text):
        text = str(text)
        text = re.sub('[^ก-๙]','',text)
        allchars = [str for str in text]
        emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI] #ลบ emoji ออก
        text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
        text = text.replace('"',"")
        text = text.replace('+',"")
        text = text.replace('/',"") #ลบคำที่ไม่ต้องการออก
        text = text.replace("!","")
        text = text.replace("​","")
        text = text.replace("#","")
        text = text.replace("@","")
        text = text.replace("_","")
        text = text.replace(":","")
        text = text.replace("(","")
        text = text.replace(")","")
        text = text.replace("-","")
        text = text.replace("*","")
        text = text.replace(".","")
        stop_word = list(thai_stopwords())
        sentence = word_tokenize(text,engine='newmm') #การตัดคำให้ออกมาเป็น list
        result = [word for word in sentence if word not in stop_word and " " not in word]
        return " ".join(result)
    
    def clean_eng(self,text):
        text = str(text)
        text = re.sub('[^a-zA-Z0-9]', ' ', text)
        text = re.sub(r'https?:\/\/.*[\r\n]', '', text,flags=re.MULTILINE) # ลบ pattern ของคำที่ไม่ต้องการออก      
        allchars = [str for str in text]
        emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI] #ลบ emoji ออก
        text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
        text = text.lower()
        text = text.split()
        ps = PorterStemmer()
        result = [ps.stem(word) for word in text if not word in set(stopwords.words('english'))]
        return ' '.join(result)
        
   
    def thai_trendy(self):

        self.consumer_key = 
        self.consumer_secret = 
        self.access_token = 
        self.access_token_secret = 

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
    
        list_t =[ ]

        try:
            #New York = 2459115  London = 44418 Thai = 23424960 usa = 23424977
            number_id = 23424960 #thailand
            trends_result = self.api.trends_place(number_id) #กำหนดว่าจะเอา trend twit ที่ประเทศไหน

            for trend in trends_result[0]['trends'][:10]: #ดึงมา 10 เทรน
                
                new_trend = trend['name'].strip('#') #ตัดอักขระหน้า/หลังสตริง
                list_t.append(new_trend)
            
            self.comboBox.addItems(list_t) #แสดง trend twit ใน combobox
           
        except tweepy.error.TweepError:
             print('There are no trending topic in Thailand')

    def world_trendy(self):
    
        self.consumer_key = 
        self.consumer_secret = 
        self.access_token = 
        self.access_token_secret = 

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
    
        list_t =[ ]

        try:
            #New York = 2459115  London = 44418 Thai = 23424960 usa = 23424977
            number_id = 23424977 #usa
            trends_result = self.api.trends_place(number_id) #กำหนดว่าจะเอา trend twit ที่ประเทศไหน

            for trend in trends_result[0]['trends'][:10]: #ดึงมา 10 เทรน
                
                new_trend = trend['name'].strip('#') #ตัดอักขระหน้า/หลังสตริง
                list_t.append(new_trend)
            
            self.comboBox2.addItems(list_t) #แสดง trend twit ใน combobox
           
        except tweepy.error.TweepError:
             print('There are no trending topic in World ')
    
 
    def OpenFile(self): #ref https://github.com/idevloping/Data-Analyze-in-gui-Pyqt5-python/blob/main/mainPyside.py

        try: #เปิดไฟล์จาก folder
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')[0]
            self.all_data = pd.read_csv(path)
        except:
            print(path)

    def dataHead(self):
        numColomn = self.spinBox.value() #รับค่าจากสปิน
        if numColomn == 0:
            NumRows = len(self.all_data.index) #นับจำนวนตาราง
        else:
            NumRows = numColomn
        #สร้างตารางจาก row และ column ของข้อมูล
        self.tableWidget.setColumnCount(len(self.all_data.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(self.all_data.columns) #เอาค่า column จากตารางทั้งหมด

        for i in range(NumRows):
            for j in range(len(self.all_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.all_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()


    
    def str_day(self): #https://www.geeksforgeeks.org/pyqt5-getting-the-text-of-selected-item-in-combobox/
        data = pd.read_csv("keyword.csv",names=['Date', 'Keyword'])
        day = data['Date'].unique()  #ข้อมูลวัน ตัดข้อมูลซ้ำออก
        self.date1.addItems(day)
        self.date2.addItems(day)

    def str_kw(self): 
        data = pd.read_csv("keyword.csv",names=['Date', 'Keyword'])
        kw = data['Keyword'].unique()  #ข้อมูลวัน ตัดข้อมูลซ้ำออก
        self.store.addItems(kw)
    
    def find_store(self):
        start = time.time()

        data = pd.read_csv('store.csv')
        key = self.store.currentText() #เอาข้อความปัจจุบัน
        date1 = self.date1.currentText()
        date2 = self.date2.currentText()
        

        c1 = data['keyword'] == key
        c2 = data['date'] == date1

        if date1 == date2  :
            check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & 
            check.to_csv('find_store.csv',index=False)
            self.hash_tag('find_store.csv')
            self.emotion('find_store.csv')
            self.word_c('find_store.csv')
            
            
        else : #https://www.youtube.com/watch?v=JpKeTfjAqKM
            df = pd.read_csv('store.csv',index_col= ['keyword','date'])
            idx = pd.IndexSlice # IndexSlice เพื่อดึงข้อมูล multi-level index
            data1 = df.loc[idx[key,[date1,date2]],:] #เข้าถึงข้อมูลผ่าน label
            data1.to_csv('find_store.csv',index=False)
            self.hash_tag('find_store.csv')
            self.emotion('find_store.csv')
            self.word_c('find_store.csv')
  
        end = time.time()
        t1 = end-start #จับเวลารัน
        self.runtime.setText("Run : " + str(t1)) 

    

#-------------เรียกใช้งานโปรแกรม--------------------------#
app = QApplication(sys.argv)
myWindow = MyWindowClass()
app.exec_()
