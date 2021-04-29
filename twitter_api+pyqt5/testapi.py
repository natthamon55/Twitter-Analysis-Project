#ref :https://www.youtube.com/watch?v=HDjc3w1W9oA
#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
# นัทธมน บุญนิธิ : 6201012620139
# search realtime & store
# use multithread
# nlp thai & english
# use pickle for help thai sentiment(train model) 
# sentiment + 5 top word + store & update data +select time to show old data
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget,QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from datetime import date
import datetime
import time
import sys
import os
import feedparser
from bs4 import BeautifulSoup
import requests
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
from pandas_datareader import data #ดึงข้อมูล data source ให้มาอยู่ในรูปแบบตาราง
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis
import re #ลบ pattern ของคำที่ไม่ต้องการออกด้วย
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import emoji #ใช้ตอนลบ อีโมจิ
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.tokenize import word_tokenize
import pickle #ช่วยในการเทรนโมเดล
import codecs #pickel part
from itertools import chain #pickel part
from nltk import NaiveBayesClassifier as nbc #สร้างโมเดล Sentiment Analysis ด้วยอัลกอริทึม Naive Bayes (ใช้ NLTK)
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


form_class = uic.loadUiType("gui.ui")[0]  #dowload gui.ui มาใช้ได้เลย

class Worker(QObject): #ทำงานกับเทรด #ห้ามยุ่งกับ gui
    print('Worker-Thread working')
    progress = pyqtSignal(str,str,str)
    finished = pyqtSignal()

    def __init__(self,key1,key2,stock,date1,date2):
        super().__init__() 
        self.key1 = key1
        self.key2 = key2
        self.stock = stock
        self.date1 = date1
        self.date2 = date2
        d1 = self.date1.split('/') #แยกเปน list string ['2021', '03', '14']
        d2 = self.date2.split('/')
        d1[2],d1[0] = d1[0],d1[2] #สลับตำแหน่งใน list เอาตน 2 มาสลับกับแรก
        d2[2],d2[0] = d2[0],d2[2]       
        self.day1 = '-'.join(d1) #เพิ่มขีด -  2021-03-14
        self.day2 = '-'.join(d2)
#-----------------pickel--------------------------#
    def loadData1(self):
        # for reading also binary mode is important
        dbfile = open('Model1', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
        return db

    def slash_tokenize(self,text):  
        self.result = text.split("#") #เพื่อแยกคำด้วย  ' # '
        self.result = list(filter(None, self.result))
        return self.result
    
#------------------------Twitter---------------------------------------#   
    def twit(self): #real time 100 tweet
        #Getting authorization
        self.consumer_key = '9GXyu3njexATouPqEvT9qvu7V'
        self.consumer_secret = 'ysgdFhBYcFclWLCC6oYiwpWCBXweQByzjfcqKs5Fm7yA7ZZdOC'
        self.access_token = '2204801114-h1YxO5itngHgvylxfAFdop7pZXYI3WzJWC1uDd6'
        self.access_token_secret = 'ZCwl7NJRHrzxgPMT9LWkQ0iYEaenwgh8rGIhAxYgXg21g'

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

        #keyword
        self.keyword = self.key1
        #date since until
        since = self.day1
        date = datetime.datetime.strptime(self.day2,'%Y-%m-%d')
        date = date + datetime.timedelta(days = 1)
        until = str(date.date())
        
        #search เพื่อเก็บ keyword
        self.search_tweet1 = [status for status in tweepy.Cursor(self.api.search, q=self.keyword).items(1)]
        #serch realtime
        self.search_tweet2 = tweepy.Cursor(self.api.search,q=self.keyword,result_type='recent',since=since,until=until,tweet_mode='extended').items(100)

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

        print('twit realtime')
        self.df.to_csv('twitter.csv')  #แปลงเป็น csv ไฟล์

        self.progress.emit(self.key1,self.key2,self.stock)

        return True
               
#-------------------------- news-----------------------------------------#
    def check_news(self):

        if self.key2 == '': #ถ้าไม่มีคำค้นหา
            print('No Search news')
            return True
            
        else:

            all_result = {} #เก็บค่าvalue ทั้งหมด

            day_list = [] #เก็บเว็บตามวันที่ค้นหา
            date_start = datetime.datetime.strptime(self.day1 ,'%Y-%m-%d') #เริ่มวันที่
            date_end = datetime.datetime.strptime(self.day2 ,'%Y-%m-%d') #จบวันที่

            while int((date_end - date_start).days) >= 0 : 
                day_list.append("web_" + date_start.strftime('%Y-%m-%d') + "_.csv") #เพิ่มวันลงlist
                date_start +=  datetime.timedelta(days = 1)
            print(day_list)
            first = True

            for news in day_list : #วนหาข่าวในวันที่เก็บตามไฟล์ web.csv
                try:
                    read_data_file = pd.read_csv(news) #อ่านไฟล์ข่าว

                    head_news = read_data_file['head_news'].str.lower() #เปลี่ยนเป็นตัวอักษรพิมพ์เล็ก
                    #เอาคำไป check ใน head_news ว่ามีหรือเปล่า
                    head_keyword = read_data_file[head_news.str.contains(self.key2, na=False)]

                    if first :#ทำให้อยู่ในรูปของ dic เก็บข้อมูล ในรูป key value
                        for column in head_keyword :
                            all_result[column] = []
                        for column in head_keyword :
                            for data in head_keyword[column] :
                                all_result[column].append(data)
                        first = False
                    else :
                        for column in head_keyword :
                            for data in head_keyword[column] :
                                all_result[column].append(data)

                except FileNotFoundError:
                    pass
            
            df = pd.DataFrame(data = all_result)
            df.to_csv('test_news.csv',index=False)
            print(df)
            return True
            
#---------------------------stock--------------------------------------------#
    def search_stock(self):   #ดึงข้อมูลราคาหุ้น จาก https://finance.yahoo.com/portfolios

        if self.stock == '' :  #ไม่มีหุ้น     
            print('no search stock')
            return True

        elif self.stock != '' : #หาหุ้น รับวันแบบ 2021-03-4
            print('search stock')
            df = data.DataReader(self.stock,data_source='yahoo',start = self.day1,end = self.day2)
            df.to_csv('stock.csv')
            self.progress.emit('','',self.stock)
            return True

#-----------------Main Search---------------------------------#
    def search_part1(self):
        
        data = pd.read_csv('store.csv') #ไฟล์ที่เก็บข้อมูล
        data1 = pd.read_csv("keyword.csv",names=['date', 'keyword']) #ไฟล์ที่เก็บ search-key แล้วเป็นการกำหนดชื่อ column ให้ตาราง
        search_key = data1['keyword'].unique() #ไม่เอาข้อมูลที่ซ้ำ

        keyword = []
        for i in search_key:
            keyword.append(i)

        c1 = data['keyword'] == self.key1
        c2 = data['date'] == self.date1

        if self.key1 == '' : #ถ้าไม่ได้หา keyword twit
            print('No Search-Twitter')
            self.check_news()#news
            self.search_stock()
            return True

                
        elif self.key1 == '' and self.key2 == '' : #หาแค่ stock
            self.search_stock()
            return True

        elif self.key1 in keyword : #in store

            try:

                if self.date1 == self.date2  : #หาแบบ 1 วัน

                    check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,มาเชื่อมกัน
                    check.to_csv('find_store.csv',index=False)
                    print('Store Part')

                    self.check_news() #news
                    self.search_stock() #stock

                    self.progress.emit(self.key1,self.key2,self.stock)
                    print('Search-Store Successful')

                    return True

                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif self.date1 != self.date2 :

                    df = pd.read_csv('store.csv')
                    colume1 = df['date'] >= self.date1
                    colume2 = df['date'] <= self.date2
                    between = df[c1 & colume1 & colume2]
                    df1 = pd.DataFrame({'keyword':between['keyword'],'date':between['date'],'text':between['text'],'hashtag':between['hashtag']})
                    df1.to_csv('find_store.csv',index=False)
                    print('Store Part')
                    self.check_news()#news
                    self.search_stock() #stock

                    self.progress.emit(self.key1,self.key2,self.stock)
                    print('Search-Store Successful')

                    return True

            except : #ไม่มีข้อมูลวันใน store ก็หา real time
                print('No date in Store Part')
                self.twit() #twitter realtime
                self.check_news()#news
                self.search_stock()
                print('Search Successful')
                return True


        else : #new keyword
            print('New Keyword')
            self.twit() #twitter realtime
            self.check_news()#news
            self.search_stock() #stock

            print('Search Successful new-word')
            return True

        self.finished.emit()
            
class MyWindowClass(QMainWindow, form_class):

    def __init__(self ,parent=None):
        super().__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        #set date (today)
        today_time = datetime.datetime.now()
        today_date = today_time.date()
        self.dateEdit.setDate(today_date)
        self.dateEdit.setMaximumDate(today_date)
        self.dateEdit2.setDate(today_date)
        self.dateEdit2.setMaximumDate(today_date)

        #keyword
        self.lineEdit.setPlaceholderText('twitter') 
        self.search_news.setPlaceholderText('news')
        
        #connect กับ ปุ่ม
        self.btnsearch.clicked.connect(self.search_part) #search twit & news
        self.btnopen.clicked.connect(self.OpenFile) #open csv
        self.btnshow.clicked.connect(self.dataHead) #show csv

        #แสดงเทรนทวิตได้เลย
        self.thai_trendy()
        self.world_trendy()

        #stock
        self.stock1.setPlaceholderText(' stock ')
  
        self.show()

#----------------------Search Twit & News & Stock-----------------------------------#
    def search_part(self):
        start = time.time()
        key1 = self.lineEdit.text() #twit
        key2 = self.search_news.text() #news
        stock =  self.stock1.text() #stock

        date1 = self.dateEdit.text() #calendar '14/03/2021'
        date2 = self.dateEdit2.text() #calendar

          
        # Step 2: Create a QThread object   
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(key1,key2,stock,date1,date2) #ตัวทำงานหลัก class Worker
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread) #ใช้เทรดเรียกมาทำงาน
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.search_part1)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.link_search)
        
        # Step 6: Start the thread
        self.thread.start()
        self.btnsearch.setEnabled(False) #ล็อคปุ่ม
        self.btnopen.setEnabled(False)
        self.btnshow.setEnabled(False)

    #วาดกราฟลง gui
    def link_search(self,key_t,key_news,key_stock):
        self.working.setText('Analysis') 

        self.hash_tag(key_t)#hashtag
        self.senti_twit(key_t) #sentiment twitter
        self.senti_news(key_news)#news
        self.plot_stock(key_stock)#stock

        self.working.setText('Done')
        self.btnsearch.setEnabled(True)
        self.btnopen.setEnabled(True)
        self.btnshow.setEnabled(True)
                           
#------------------------twitter sentiment & hashtag ---------------------#
    def senti_twit(self,search):

        if search == '':
            pass

        elif re.match('[ก-๙]',search) !=  None:

            self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent2.png);')

        else :
            self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent1.png);')

    def hash_tag(self,search): #top hashtag

        if search == '':
            pass
        
        else :
            self.topw.setStyleSheet('border-image: url(C:/software/software2/pic/top.png);')
        
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

            for trend in trends_result[0]['trends'][:20]: #ดึงมา 10 เทรน
                
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

            for trend in trends_result[0]['trends'][:20]: #ดึงมา 10 เทรน
                
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

#-----------------------------Sentiment news--------------------------------------------------------#
    def senti_news(self,search):
        if search == '':
            pass

        elif re.match('[ก-๙]',search) !=  None:
            self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/thnews_sent.png);')
        else :

            self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/ennews_sent.png);')

#------------------------stock------------------------------------------#    
    def plot_stock(self,search): #https://saralgyaan.com/posts/python-candlestick-chart-matplotlib-tutorial-chapter-11/
        #abroad stock ex fb,amzn,aapl,goog,msft, TSLA
        #crypto ex XRP-USD , BTC-USD ,XLM-USD,ADA-USD,DOT1-USD,DOGE-USD
        #thai stock ex PTT.BK,AOT.BK,SCC.BK,KTB.BK,SCB.BK,CPALL.BK,OR.BK
        #ชื่อย่อหุ้นไทยจะมีชื่อ .BK ตามหลังชื่อย่อหุ้น
        if search == '':
            pass
        else :
            self.graph.setStyleSheet('border-image: url(C:/software/software2/pic/stock.jpg);')

#-------------เรียกใช้งานโปรแกรม--------------------------#
if __name__ == '__main__': #ถ้าใส่จะ run แค่ในไฟล์นี้เท่านั้น
    app = QApplication(sys.argv)
    myWindow = MyWindowClass()
    app.exec_()

