#ref :https://www.youtube.com/watch?v=HDjc3w1W9oA
#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
# นัทธมน บุญนิธิ : 6201012620139
# search realtime & store
# nlp thai & english
# sentiment + 5 top word + store & update data +select time to show old data
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget,QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from datetime import date
import time
from time import sleep
import csv 
import sys
import os
from bs4 import BeautifulSoup
import requests
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
from pandas_datareader import data #ดึงข้อมูล data source ให้มาอยู่ในรูปแบบตาราง
import seaborn as sns #สำหรับการ plot ข้อมูลในรูปแบบต่าง ๆ
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis
from wordcloud import WordCloud #ใช้แสดงผลกลุ่มคำที่เจอบ่อย
import re #ลบ pattern ของคำที่ไม่ต้องการออกด้วย
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import emoji #ใช้ตอนลบ อีโมจิ
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.tokenize import word_tokenize
import codecs
from itertools import chain
from nltk import NaiveBayesClassifier as nbc #สร้างโมเดล Sentiment Analysis ด้วยอัลกอริทึม Naive Bayes (ใช้ NLTK)
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


form_class = uic.loadUiType("gui.ui")[0]  #dowload gui.ui มาใช้ได้เลย

class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        #keyword
        self.lineEdit.setPlaceholderText('twitter') 
        self.search_news.setPlaceholderText('news')
        
        #connect กับ ปุ่ม
        self.btnsearch.clicked.connect(self.search_twit) #search twit & news
        self.btnopen.clicked.connect(self.OpenFile) #open csv
        self.btnshow.clicked.connect(self.dataHead) #show csv
        self.btnstock.clicked.connect(self.search_stock) #search stock

        #แสดงเทรนทวิตได้เลย
        self.thai_trendy()
        self.world_trendy()

        #store
        self.str_day()

        #stock
        self.stock1.setPlaceholderText(' Search Stock ')
        self.stock2.setPlaceholderText('Start Y-M-D')
        self.stock3.setPlaceholderText('End Y-M-D ')
        

        self.show()

###--------------------------Twitter ----------------------------------###     
    def twit(self,keyword1,keyword2): #real time
        #Getting authorization
        self.consumer_key = '9GXyu3njexATouPqEvT9qvu7V'
        self.consumer_secret = 'ysgdFhBYcFclWLCC6oYiwpWCBXweQByzjfcqKs5Fm7yA7ZZdOC'
        self.access_token = '2204801114-h1YxO5itngHgvylxfAFdop7pZXYI3WzJWC1uDd6'
        self.access_token_secret = 'ZCwl7NJRHrzxgPMT9LWkQ0iYEaenwgh8rGIhAxYgXg21g'

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

        #keyword
        self.keyword = keyword1

        #search เพื่อเก็บ keyword
        self.search_tweet1 = [status for status in tweepy.Cursor(self.api.search, q=self.keyword).items(1)]
        #serch realtime
        self.search_tweet2 = tweepy.Cursor(self.api.search,q=self.keyword,result_type='recent',tweet_mode='extended').items(50)

        #บันทึกไฟล์ keyword ไว้ check ว่าวันนี้ค้นหาคำว่าอะไรไปบ้าง
        self.data = pd.DataFrame(columns = ['Date','Keyword'])
        for twit in self.search_tweet1:
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

        #news
        self.find_news('top10.csv',keyword2)


    def str_day(self): #https://www.geeksforgeeks.org/pyqt5-getting-the-text-of-selected-item-in-combobox/
        data = pd.read_csv("keyword.csv",names=['Date', 'Keyword'])
        day = data['Date'].unique()  #ข้อมูลวัน ตัดข้อมูลซ้ำออก
        self.date1.addItems(day)
        self.date2.addItems(day)

    
#----------------------Search Part-----------------------------------#
    def search_twit(self):
        start = time.time()
        data = pd.read_csv('store.csv') #ไฟล์ที่เก็บข้อมูล

        key1 = self.lineEdit.text() #twit
        key2 = self.search_news.text() #news

        date1 = self.date1.currentText()
        date2 = self.date2.currentText()

        c1 = data['keyword'] == key1
        c2 = data['date'] == date1

        keyword = []
        for i in data['keyword']:
            keyword.append(i)

        try :
        
            if key1 in keyword :

                if date1 == date2  : #หาแบบ 1 วัน
                    check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,าเชื่อมกัน
                    check.to_csv('find_store.csv',index=False)
                    self.hash_tag('find_store.csv') #top hashtag
                    self.emotion('find_store.csv')  #sentimenr
                    self.find_news('find_store.csv',key2) #news
                    print('Search Successful1')

                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น
                elif date1 != date2 :#https://www.youtube.com/watch?v=JpKeTfjAqKM
                    df = pd.read_csv('store.csv')
                    colume1 = df['date'] >= date1
                    colume2 = df['date'] <= date2
                    between = df[c1 & colume1 & colume2]
                    df1 = pd.DataFrame({'keyword':between['keyword'],'date':between['date'],'text':between['text'],'hashtag':between['hashtag']})
                    df1.to_csv('find_store.csv',index=False)
                    self.hash_tag('find_store.csv')
                    self.emotion('find_store.csv')
                    self.find_news('find_store.csv',key2) #news
                    print('Search Successful2')

                else:
                    self.twit(key1,key2)
                    print('Search Successful3')


        except :

            self.twit(key1,key2)
            print('Search Successful')


        end = time.time()
        t1 = end-start #จับเวลารัน
        self.runtime.setText("Run : " + str(t1)) 


#------------------------twitter sentiment---------------------#
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
        data = {
        "Positive + ": (pos, QColor("#66ff99")),
        "Negative -": (neg, QColor("#ff6666")),
        "Neutral  0": (neu, QColor("#ffff66")),}

        se = QPieSeries()
        for name, (value, color) in data.items():
            _slice = se.append(name, value)
            _slice.setBrush(color)

        chart = QChart()
        chart.addSeries(se)
        chart.setTitle('Twitter Sentiment')

        chartview = QChartView(chart)
        chartview.setGeometry(0,0,521,421)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.saveapi = QPixmap(chartview.grab())
        self.saveapi.save('C:/software/software2/pic/sent.png','PNG')
        self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent.png);')

    def hash_tag(self,path): #top hashtag
        df = pd.read_csv(path)
        hastag_data = df["hashtag"].dropna() #ลบข้อมูลที่ว่างออก
        vectorizer = CountVectorizer(tokenizer=self.slash_tokenize)#สอนให้เป็นตัวตัดคำ (tokenizer)
        #เพื่อสอน vectorizer ว่ามีคำอะไรบ้างใน data และแปลงข้อมูล data ให้อยู่ในรูปแบบเดียวกับเราสอนให้ vectorizer
        transformed_data = vectorizer.fit_transform(hastag_data)
        hash_tag_cnt_df= pd.DataFrame(columns = ['word', 'count']) #เก็บข้อมูลลง df
        hash_tag_cnt_df['word'] = vectorizer.get_feature_names() # เพื่อให้ได้ข้อมูลคำทั้งหมดที่สอน vectorizer ไป 
        hash_tag_cnt_df['count'] = np.ravel(transformed_data.sum(axis=0))#นับจำนวนคำที่แปลงแล้ว
        data2 = hash_tag_cnt_df.sort_values(by=['count'], ascending=False).head(5)
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

    def slash_tokenize2(self,text):  
        self.result = text.split(" ") #เพื่อแยกคำด้วย  '  '
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
        
#-----------------------------------Trend Twitter-------------------------------------------------#
    def thai_trendy(self):

        self.consumer_key = '9GXyu3njexATouPqEvT9qvu7V'
        self.consumer_secret = 'ysgdFhBYcFclWLCC6oYiwpWCBXweQByzjfcqKs5Fm7yA7ZZdOC'
        self.access_token = '2204801114-h1YxO5itngHgvylxfAFdop7pZXYI3WzJWC1uDd6'
        self.access_token_secret = 'ZCwl7NJRHrzxgPMT9LWkQ0iYEaenwgh8rGIhAxYgXg21g'

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
    
        self.consumer_key = '9GXyu3njexATouPqEvT9qvu7V'
        self.consumer_secret = 'ysgdFhBYcFclWLCC6oYiwpWCBXweQByzjfcqKs5Fm7yA7ZZdOC'
        self.access_token = '2204801114-h1YxO5itngHgvylxfAFdop7pZXYI3WzJWC1uDd6'
        self.access_token_secret = 'ZCwl7NJRHrzxgPMT9LWkQ0iYEaenwgh8rGIhAxYgXg21g'

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
    
 #---------------------------------Table----------------------------------------------------------------#
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



#####-----------------------------english news--------------------------------------------------------#### 
    def get_article(self,page):
        #access article information from html
        headline = page.find('h4', 's-title').text  #กรองเอาเฉพาะข้อความที่ต้องการ
        source = page.find("span", 's-source').text #แหล่งที่มา
        posted = page.find('span', 's-time').text.replace('·', '').strip() #ใช้สำหรับตัดอักขระด้านหน้าและด้านหลังของสตริง
        raw_link = page.find('a').get('href') #link
        cont = page.find('p', 's-desc').text.strip()
        unquoted_link = requests.utils.unquote(raw_link)
        pattern = re.compile(r'RU=(.+)\/RK')
        clean_link = re.search(pattern, unquoted_link).group(1)  
        article = (headline, source, posted,cont, clean_link)
        return article

    def get_the_news(self,search): #https://www.youtube.com/watch?v=hMxFnVVYGDk

        #ดึงข้อมูลจาก yahoo news
        headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'th-TH,th;q=0.9',
                'referer': 'https://news.yahoo.com/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAFJNOkCmzmvFF617as2nr7u5OVwBzw2otAjLeNN0VnQlXjv58oUkIsPAzKCmlHIP5O8LH0IANGlUJKToWX4BwoBl2SH_K11CvQh6kt4xCSfXO8EmrphDKHC27jRWXUAVOcEvWBbY1l5i39PqsqMFTOU5Iyyqtvs3UehXmtyjRoZk',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
            }

        web = 'https://news.search.yahoo.com/search?p={}'
        url = web.format(search) #คำที่ต้องการค้นหา แล้วใช้ .format เชื่อมคำเหมือนเข้า link 
        articles = []
        links = set()
        
        response = requests.get(url, headers=headers) #ดึงข้อมูลทั้งหมดจากหน้าเว็บ
        soup = BeautifulSoup(response.text, 'html.parser') #อ่านข้อมูลทั้งหมดในรูปแบบ html
        pages = soup.find_all('div', 'NewsArticle') #ค้นหาว่าจะดึงส่วนไหนมาแสดงจากเว็บไซต์
            
        # extract articles from page
        for p in pages:
            article = self.get_article(p) #เข้าถึงข้อมูล และclean ข้อมูล html
            link = article[-1]
            if not link in links:
                links.add(link)
                articles.append(article) 
            
            
        # save article data
        with open('eng_news.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Headline', 'Source', 'Posted','Content' ,'Link'])
            writer.writerows(articles)
        
        df = pd.read_csv('eng_news.csv')
        self.textnews.clear() #clear old news
        for i in df['Headline']:
            self.textnews.append('-'+i+'\n') #add news in textbrowser

        #plot pie chart
        self.eng_sent('eng_news.csv')

    #eng sentiment
    def eng_sent(self,path): #sentiment eng_news
        #sentiment
        df = pd.read_csv(path)
        pos = 0
        neg = 0
        neu = 0
        for tweet in df['Headline']:
            analysis = TextBlob(tweet)
            if analysis.sentiment[0]>0:  #1 is positive
                    pos +=  1
            elif analysis.sentiment[0]<0: #-1 is a negative
                    neg +=  1
            else:   # 0 is independent  
                    neu +=  1
        data = {
        "Positive + ": (pos, QColor("#66ff99")),
        "Negative -": (neg, QColor("#ff6666")),
        "Neutral  0": (neu, QColor("#ffff66")),}

        se = QPieSeries()
        for name, (value, color) in data.items():
            _slice = se.append(name, value)
            _slice.setBrush(color)

        chart = QChart()
        chart.addSeries(se)
        chart.setTitle('ENG-News Sentiment')

        chartview = QChartView(chart)
        chartview.setGeometry(0,0,521,421)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.saveapi = QPixmap(chartview.grab())
        self.saveapi.save('C:/software/software2/pic/sent2.png','PNG')
        self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/sent2.png);')

###-------------------- Thai news-----------------------####
    def get_thai_article(self,page):
        headline = page.find('span', 'jsx-2430232205 jsx-3959658973 text-color-news').text  #กรองเอาเฉพาะข้อความที่ต้องการ
        link = page.find('a').get('href') #link
        time = page.find('time').get('datetime')  #date
        cont = page.find('p', 'jsx-2430232205 jsx-3959658973 description').text #content

        article = (headline,time,cont,link)
        return article

    def get_thai_news(self,search):
        
        web = 'https://www.sanook.com/news/search/{}/'
        url = web.format(search)

        articles = []
        links = set()

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = soup.find_all('div','jsx-4244751374')

        # extract articles from page
        for p in pages:
            article = self.get_thai_article(p) #เข้าถึงข้อมูล และclean ข้อมูล html
            link = article[-1]
            if not link in links:
                links.add(link)
                articles.append(article)
        
        with open('thai_news.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Headline','Date','Content' ,'Link'])
            writer.writerows(articles)

        df = pd.read_csv('thai_news.csv')
        self.textnews.clear() #clear old news
        for i in df['Headline'].unique():
            self.textnews.append('-'+i+'\n') #add news in textbrowser

        # plot pie chart
        #self.thai_sent('thai_news.csv')

    #thai sentiment
    def thai_sent(self,path):
        
        df = pd.read_csv(path)
        
        pos = 0
        neg = 0
        neu = 0
        # pos.txt
        with codecs.open('pos.txt', 'r', "utf-8") as f:
            lines1 = f.readlines()
        listpos=[e1.strip() for e1 in lines1]
        f.close() # ปิดไฟล์

        # neu.txt
        with codecs.open('neu.txt', 'r', "utf-8") as f:
            lines2 = f.readlines()
        listneu=[e2.strip() for e2 in lines2]
        f.close() # ปิดไฟล์

        # neg.txt
        with codecs.open('neg.txt', 'r', "utf-8") as f:
            lines3 = f.readlines()
        listneg=[e3.strip() for e3 in lines3]
        f.close() # ปิดไฟล์

        pos1=['pos']*len(listpos)
        neu1=['neu']*len(listneu)
        neg1=['neg']*len(listneg)

        #[(ประโยค,pos / neg  )]
        training_data = list(zip(listpos,pos1))+ list(zip(listneu,neu1))+ list(zip(listneg,neg1))

        #ทำการแบ่งคำออกจากประโยคโดยใช้ PyThaiNLP แล้วหาเวกเตอร์คำ
        vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in training_data]))
        feature_set = [({i:(i in word_tokenize(sentence.lower())) for i in vocabulary},tag) for sentence, tag in training_data]

        #ทำการ train โมเดลด้วยอัลกอริทึม Naive Bayes โดยใช้ NLTK
        classifier = nbc.train(feature_set)

        for news in df['Headline']:

            sentence = news
            featurized_test_sentence =  {i:(i in word_tokenize(sentence.lower())) for i in vocabulary}
            
            #ทำการ train โมเดลด้วยอัลกอริทึม Naive Bayes โดยใช้ NLTK
            if classifier.classify(featurized_test_sentence) == 'pos':
                pos += 1
            elif classifier.classify(featurized_test_sentence) == 'neg':
                neg += 1
            else:
                neu += 1

        data = {
        "Positive + ": (pos, QColor("#66ff99")),
        "Negative -": (neg, QColor("#ff6666")),
        "Neutral  0": (neu, QColor("#ffff66")),}

        se = QPieSeries()
        for name, (value, color) in data.items():
            _slice = se.append(name, value)
            _slice.setBrush(color)

        chart = QChart()
        chart.addSeries(se)
        chart.setTitle('Thai-News Sentiment')

        chartview = QChartView(chart)
        chartview.setGeometry(0,0,521,421)
        chartview.setRenderHint(QPainter.Antialiasing)


        self.saveapi = QPixmap(chartview.grab())
        self.saveapi.save('C:/software/software2/pic/news_word.png','PNG')
        self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/news_word.png);')


##--------------------Th/Eng news-------------------------------------##
    def find_news(self,path,search) :
        df = pd.read_csv(path)
        t = df['text'] #ข้อความทวิตในตาราง
        
        for item in t : 
    
            if re.match('[ก-๙]',item) !=  None:
                self.get_thai_news(search)
            

            else :
                self.get_the_news(search)
                

###------------------------stock------------------------------------------###

    def search_stock(self):   #ดึงข้อมูลราคาหุ้น จาก https://finance.yahoo.com/portfolios

        start = time.time()

        stock =  self.stock1.text()
        #s = self.stock2.text() #start
        #e = self.stock3.text()  #end

        s = self.dateEdit.date().toPydate()
        e = self.dateEdit1.date().toPydate()

        df = data.DataReader(stock,data_source='yahoo',start = s,end = e)
        df.to_csv('stock.csv')
        #plot graph
        self.plot_stock('stock.csv')
        plt.close('all') #closes all the figure windows

        end = time.time()
        t1 = end-start #จับเวลารัน
        self.runtime.setText("Run : " + str(t1)) 

    
    def plot_stock(self,path):
        #abroad stock ex fb,amzn,aapl,goog,msft, TSLA
        #crypto ex XRP-USD , BTC-USD ,XLM-USD,ADA-USD,DOT1-USD,DOGE-USD
        #thai stock ex PTT.BK,AOT.BK,SCC.BK,KTB.BK,SCB.BK,CPALL.BK,OR.BK
        #ชื่อย่อหุ้นไทยจะมีชื่อ .BK ตามหลังชื่อย่อหุ้น
        df = pd.read_csv(path)
        date = df['Date']
        adj = df['Adj Close']

        plt.plot(date,adj, 'g--')
        plt.xlabel('DATE')
        plt.ylabel('Adj Close')
        plt.title(self.stock1.text()) 
        plt.savefig('C:/software/software2/pic/stock.jpg')
        self.graph.setStyleSheet('border-image: url(C:/software/software2/pic/stock.jpg);')

#-------------เรียกใช้งานโปรแกรม--------------------------#
app = QApplication(sys.argv)
myWindow = MyWindowClass()
app.exec_()