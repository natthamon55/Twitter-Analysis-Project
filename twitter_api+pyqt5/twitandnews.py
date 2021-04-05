#ref :https://www.youtube.com/watch?v=HDjc3w1W9oA
#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
# นัทธมน บุญนิธิ : 6201012620139
# search realtime & store
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
import pickle #ช่วยในการเทรนโมเดล
import datetime
import time
import csv 
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
import codecs
from itertools import chain
from nltk import NaiveBayesClassifier as nbc #สร้างโมเดล Sentiment Analysis ด้วยอัลกอริทึม Naive Bayes (ใช้ NLTK)
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


form_class = uic.loadUiType("gui.ui")[0]  #dowload gui.ui มาใช้ได้เลย

class MyWindowClass(QMainWindow, form_class):

    def __init__(self):
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

###--------------------------Twitter ----------------------------------###     
    def twit(self,keyword1,s,e): #real time 100 tweet
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
        #date
        since = s
        date = datetime.datetime.strptime(e,'%Y-%m-%d')
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
        

        print('twit realtime')
        self.df.to_csv('twitter.csv')  #แปลงเป็น csv ไฟล์
        self.df2.to_csv('store.csv', mode = 'a',header= ['keyword','date','text','hashtag','rt','fav'] , encoding='utf-8',index= True) # ไฟล์ store data เพิ่มข้อมูลต่อท้ายในไฟล์ csv 

        #show top 10 data
        data1 = self.df.drop_duplicates("text").sort_values(by=['retweet_count'], ascending=False).head(10)[['text','retweet_count']]
        data1.to_csv('top10.csv',index= True)

        #analysis
        self.hash_tag('twitter.csv')
        self.sent_twit(keyword1,'twitter.csv') #sentiment twitter

#----------------------Search Twit & News & Stock-----------------------------------#
    def search_part(self):
        
        start = time.time()

        data = pd.read_csv('store.csv') #ไฟล์ที่เก็บข้อมูล
        data1 = pd.read_csv("keyword.csv",names=['date', 'keyword']) #ไฟล์ที่เก็บ search-key แล้วเป็นการกำหนดชื่อ column ให้ตาราง
        search_key = data1['keyword'].unique() #ไม่เอาข้อมูลที่ซ้ำ

        key1 = self.lineEdit.text() #twit
        key2 = self.search_news.text() #news
        stock =  self.stock1.text() #stock

        date1 = self.dateEdit.text() #calendar '14/03/2021'
        date2 = self.dateEdit2.text() #calendar

        d1 = date1.split('/') #แยกเปน list string ['2021', '03', '14']
        d2 = date2.split('/')
        d1[2],d1[0] = d1[0],d1[2] #สลับตำแหน่งใน list เอาตน 2 มาสลับกับแรก
        d2[2],d2[0] = d2[0],d2[2]       
        day1 = '-'.join(d1) #เพิ่มขีด -  2021-03-14
        day2 = '-'.join(d2)

        keyword = []
        for i in search_key:
            keyword.append(i)

        c1 = data['keyword'] == key1
        c2 = data['date'] == date1

        if key1 == '' : #ถ้าไม่ได้หา keyword twit
            print('No Search-Twitter')
            self.check_news(key2,date1,date2)#news
            self.search_stock(stock,day1,day2)
                
        elif key1 == '' and key2 == '' : #หาแค่ stock
            self.search_stock(stock,day1,day2)

        elif key1 in keyword : #in store

            try:

                if date1 == date2  : #หาแบบ 1 วัน

                    check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,มาเชื่อมกัน
                    check.to_csv('find_store.csv',index=False)
                    print('Store Part')
                    self.hash_tag('find_store.csv') #top hashtag
                    self.sent_twit(key1,'find_store.csv')  #sentiment twitter
                    self.check_news(key2,date1,date2) #news
                    self.search_stock(stock,day1,day2) #stock
                    print('Search-Store Successful')

                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif date1 != date2 :

                    df = pd.read_csv('store.csv')
                    colume1 = df['date'] >= date1
                    colume2 = df['date'] <= date2
                    between = df[c1 & colume1 & colume2]
                    df1 = pd.DataFrame({'keyword':between['keyword'],'date':between['date'],'text':between['text'],'hashtag':between['hashtag']})
                    df1.to_csv('find_store.csv',index=False)
                    print('Store Part')
                    self.hash_tag('find_store.csv')
                    self.sent_twit(key1,'find_store.csv')  #sentiment twitter
                    self.check_news(key2,date1,date2)#news
                    self.search_stock(stock,day1,day2) #stock
                    print('Search-Store Successful')

            except : #ไม่มีข้อมูลวันใน store ก็หา real time
                print('No date in Store Part')
                self.twit(key1,day1,day2) #twitter realtime
                self.check_news(key2,date1,date2)#news
                self.search_stock(stock,day1,day2)
                print('Search Successful')

        else : #new keyword
            print('New Keyword')
            self.twit(key1,day1,day2) #twitter realtime
            self.check_news(key2,date1,date2)#news
            self.search_stock(stock,day1,day2) #stock
            print('Search Successful new-word')

        end = time.time()
        t1 = end-start #จับเวลารัน
        self.runtime.setText(str(t1)) 
    
    def check_news(self,search,date1,date2):
        
        if  search == '':
            print('No news to find')

        elif  re.match('[ก-๙]',search) !=  None: #เทียบภาษา หาข่าวไทย
            print('Thai News working')
            data = pd.read_csv('store_thai_news.csv') #ไฟล์ที่เก็บข้อมูล
            data1 = pd.read_csv("keythai_news.csv",names=['date', 'keyword']) #ไฟล์ที่เก็บ search-key แล้วเป็นการกำหนดชื่อ column ให้ตาราง
            search_key = data1['keyword'].unique() #ไม่เอาข้อมูลที่ซ้ำ

            keyword = [] #ไว้ check คำ
            for i in search_key:
                keyword.append(i)
     
            check = []
            colume1 = data1['date'] >= date1 #มาจาก ไฟล์keyword ที่เก็บไว้
            colume2 = data1['date'] <= date2
            between = data1[colume1 & colume2]
            #ไว้ check วันกับคำที่เคยหา เป็นคู่ๆ โดยเก็บเป็นชุดข้อมูลวันที่และคำที่เคยค้น
            for i,j in zip(between['date'],between['keyword']): #วนลูป i,j พร้อมกัน
                op = (i,j)
                check.append(op)
            print(f'Check:{check}')
            
            try :

                if date1 == date2  : #หาแบบ 1 วัน
                    op1 = (date1,search)
                    print(f'Data: {op1}')

                    if op1 in check: #ถ้าวันกับคำ อยู่ในวันที่ check 
                        print('Store Thai News')
                        c1 = data['Keyword'] == search
                        c2 = data['Date'] == date1
                        check = data[c1 & c2] #ถ้ามีหลายเงื่อนไขเราสามารถใช้ & ,มาเชื่อมกัน
                        check.to_csv('find_news.csv',index=False)
                        self.thai_sent('find_news.csv')

                        df = pd.read_csv('find_news.csv')
                        self.textnews.clear() #clear old news
                        for i in df['Headline'].head(20):
                            self.textnews.append('-'+i+'\n') #add news in textbrowser
                        print('done1')

                    elif op1 not in check:#ถ้าวันกับคำ ไม่อยู่ในวันที่ check
                        print('Find thai-news realtime no date in store')
                        self.find_news(search)
                   
                    elif search not in keyword: #ไม่เคยหาคำนั้นมาก่อน
                        print('Find news keyword')
                        self.find_news(search)

                    else : #กรณีอื่นๆ
                        print('find thai news real time')
                        self.find_news(search)
                                                
                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif date1 != date2 :  
                    op1 = (date1,search)
                    op2 = (date2,search)
                    print(f'Data : {op1},{op2}')

                    if search in keyword and op1 in check or op2 in check: #เคยหาคำนั้นมาแล้ว และมีวันและคำอยู่ใน check
                        print('Store thai News')
                        df = pd.read_csv('store_thai_news.csv')
                        c1 = data['Keyword'] == search
                        c2 = df['Date'] >= date1
                        c3 = df['Date'] <= date2
                        between1 = df[c1 & c2 & c3]
                        df1 = pd.DataFrame({'keyword':between1['Keyword'],'date':between1['Date'],'Headline':between1['Headline'],'Content':between1['Content'],'Link':between1['Link']})
                        df1.to_csv('find_news.csv',index=False)
                        self.thai_sent('find_news.csv')

                        df2 = pd.read_csv('find_news.csv')
                        self.textnews.clear() #clear old news
                        for i in df2['Headline'].head(20):
                            self.textnews.append('-'+i+'\n') #add news in textbrowser
                        print('done2')

                    elif op1 not in check or op2 not in check: #เคยหาคำนั้นแต่ไม่มีวัน
                        print('Find thai-news realtime no date in store')
                        self.find_news(search)

                    elif op1 not in check and op2 not in check : #เคยหาคำนั้นแต่ไม่มีวัน
                        print('Find thai-news realtime no date in store')
                        self.find_news(search)

                    elif search not in keyword: #ไม่เคยหาคำนั้น
                        print('Find thai-news new-keyword realtime')
                        self.find_news(search)
                    
                    else : #กรณีอื่นๆ
                        print('find thai-news real time')
                        self.find_news(search)
                
            except : #กรณีเกิด error

                print('Find thai news realtime')
                self.find_news(search)
          

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
            #ไว้ check วันกับคำที่เคยหา เป็นคู่ๆ โดยเก็บเป็นชุดข้อมูลวันที่และคำที่เคยค้น
            for i,j in zip(between['date'],between['keyword']): #วนลูป i,j พร้อมกัน
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
                        self.eng_sent('find_news.csv')

                        df = pd.read_csv('find_news.csv')
                        self.textnews.clear() #clear old news
                        for i in df['Headline'].head(20):
                            self.textnews.append('-'+i+'\n') #add news in textbrowser
                        print('done1')

                    elif op1 not in check:
                        print('Find eng-news realtime no date in store')
                        self.find_news(search)

                    elif search not in keyword:
                        print('Find eng-news new-keyword realtime')
                        self.find_news(search)
                    
                    else :
                        print('find eng-news realtime')
                        self.find_news(search)
                                                                        
                #หาแบบหลายวัน  แบบกำหนดขอบเขตวันมีวันไหนเอาวันนั้น กำหนดเวลา
                elif date1 != date2 :
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
                        self.eng_sent('find_news.csv')

                        df2 = pd.read_csv('find_news.csv')
                        self.textnews.clear() #clear old news
                        for i in df2['Headline'].head(20):
                            self.textnews.append('-'+i+'\n') #add news in textbrowser
                        print('done2')
                    
                    elif op1 not in check or op2 not in check :
                        print('Find eng-news realtime no date in store')
                        self.find_news(search)
                    
                    elif op1 not in check and op2 not in check :
                        print('Find eng-news realtime no date in store')
                        self.find_news(search)

                    elif search not in keyword:
                        print('Find eng-news new-keyword realtime')
                        self.find_news(search)

                    else :
                        print('find eng-news real time')
                        self.find_news(search)

            except :

                print('Find eng-news realtime')
                self.find_news(search)

#-----------------pickel--------------------------#
    def pick_thaisent(self):
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

        training_data = list(zip(listpos,pos1)) + list(zip(listneu,neu1)) + list(zip(listneg,neg1))
        vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in training_data]))
        feature_set = [({i:(i in word_tokenize(sentence.lower())) for i in vocabulary},tag) for sentence, tag in training_data]
        classifier = nbc.train(feature_set)
        total = (classifier,vocabulary)
        return total

    def storeData(self): 
        # database 
        db = self.pick_thaisent()
        # Its important to use binary mode 
        dbfile = open('Model1', 'wb') 
        # source, destination
        pickle.dump(db, dbfile)
        dbfile.close()

    def loadData(self):
        # for reading also binary mode is important
        dbfile = open('Model1', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
        return db

#------------------------twitter sentiment & hashtag ---------------------#
    def sent_twit(self,search,path):

        if re.match('[ก-๙]',search) !=  None:
            df = pd.read_csv(path)
        
            P = self.loadData() #pickle เรียกไฟล์โหลดมา
            pos = 0
            neg = 0
            neu = 0
            for news in df['text']:

                sentence = news
                featurized_test_sentence =  {i:(i in self.clean_thai(sentence.lower())) for i in P[1]}
                
                #ทำการ train โมเดลด้วยอัลกอริทึม Naive Bayes โดยใช้ NLTK
                if P[0].classify(featurized_test_sentence) == 'pos':
                    pos += 1
                elif P[0].classify(featurized_test_sentence) == 'neg':
                    neg += 1
                else:
                    neu += 1

            print('Thai-twitter Sentiment')
            print("Total Positive : ", pos)
            print("Total Negative : ", neg)
            print("Total Neutral :", neu)

            labels = ['positive','negative','neutral']
            sizes =  [pos,neg,neu]
            explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90 , colors=['green', 'red', 'yellow'])
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Thai-twitter Sentiment')
            plt.savefig('C:/software/software2/pic/sent2.png')
            self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent2.png);')

        else :

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

            print('ENG-twitter Sentiment')
            print("Total Positive : ", pos)
            print("Total Negative : ", neg)
            print("Total Neutral :", neu)

            labels = ['Positive','Negative','Neutral']
            sizes =  [pos,neg,neu]
            explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90 , colors=['green', 'red', 'yellow'])
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('ENG-twitter Sentiment')
            plt.savefig('C:/software/software2/pic/sent1.png')
            self.sent.setStyleSheet('border-image: url(C:/software/software2/pic/sent1.png);')

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

#-----------------------------clean word------------------------------------#              
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

#####-----------------------------English news--------------------------------------------------------#### 
    def get_article(self,page):
        #access article information from html
        '''
        Get the text from html and do some cleaning
        '''
        soup = BeautifulSoup(page)
        text = soup.get_text()
        text = text.replace('\xa0', ' ')
        return text


    def get_the_news(self,search): #https://towardsdatascience.com/how-to-get-the-latest-covid-19-news-using-google-news-feed-950d9deb18f1
        #ดึงข้อมูลจาก google news
        web = "http://news.google.com/news?q={}-19&hl=en-US&sort=date&gl=US&num=100&output=rss"
        url = web.format(search)
        feeds = feedparser.parse(url).entries #Parse the URL

        data = pd.DataFrame(columns = ['Date','Keyword'])
        if search != ' ' :
            key = search
            today = date.today()
            d = today.strftime("%d/%m/%Y")
            add_c = pd.Series([d,key], index=data.columns)
            data = data.append(add_c,ignore_index=True)

        data.to_csv('keyeng_news.csv', mode = 'a',header = False , encoding='utf-8',index= False)
        #real time
        df1 = pd.DataFrame(columns= ['Keyword','Date','Headline','Posted', 'Content', 'Link'])
        #store news
        df2 = pd.DataFrame(columns= ['Keyword','Date','Headline','Posted', 'Content', 'Link'])
        for f in feeds:   
            cont = self.get_article(f.get("description", ""))
            post = f.get("published", "")
            title = f.get("title", "")
            link =  f.get("link", "")
            keyword = search
            today = date.today()
            d1 = today.strftime("%d/%m/%Y") #เวลาปจบ
            
            #real time
            new_column = pd.Series([keyword,d1,title,post,cont,link], index=df1.columns)
            df1 = df1.append(new_column,ignore_index=True)
            #store 
            new_column1 = pd.Series([keyword,d1,title,post,cont,link], index=df2.columns)
            df2 = df2.append(new_column1,ignore_index=True)

        df1.to_csv('eng_news.csv')
        df2.to_csv('store_eng_news.csv', mode = 'a',header= ['Keyword','Date','Headline','Posted', 'Content', 'Link'] , encoding='utf-8',index= True)

        
        df = pd.read_csv('eng_news.csv')
        self.textnews.clear() #clear old news
        for i in df['Headline'].head(20):
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

        print('ENG-News Sentiment')
        print("Total Positive : ", pos)
        print("Total Negative : ", neg)
        print("Total Neutral :", neu)

        labels = ['Positive','Negative','Neutral']
        sizes =  [pos,neg,neu]
        explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90 , colors=['green', 'red', 'yellow'])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('ENG-News Sentiment')
        plt.savefig('C:/software/software2/pic/ennews_sent.png')
        self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/ennews_sent.png);')

###-------------------- Thai news-----------------------####
    def get_thai_news(self,search):
        
        web = 'https://www.sanook.com/news/search/{}/'
        url = web.format(search)

        articles = []
        links = set()

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = soup.find_all('div','jsx-4244751374')

        data = pd.DataFrame(columns = ['Date','Keyword'])
        if search != ' ' :
            key = search
            today = date.today()
            d = today.strftime("%d/%m/%Y")
            add_c = pd.Series([d,key], index=data.columns)
            data = data.append(add_c,ignore_index=True)

        data.to_csv('keythai_news.csv', mode = 'a',header = False , encoding='utf-8',index= False)

        #real time
        df1 = pd.DataFrame(columns= ['Keyword','Date','Headline','Posted', 'Content', 'Link'])
        #store news
        df2 = pd.DataFrame(columns= ['Keyword','Date','Headline','Posted', 'Content', 'Link'])

        for p in pages :
            headline = p.find('span', 'jsx-2430232205 jsx-180597169 text-color-news').text  #กรองเอาเฉพาะข้อความที่ต้องการ
            link = p.find('a').get('href') #link
            time = p.find('time').get('datetime')  #date
            cont = p.find('p', 'jsx-2430232205 jsx-180597169 description').text #content
            keyword = search
            today = date.today()
            d1 = today.strftime("%d/%m/%Y") #เวลาปจบ

            #real time
            new_column = pd.Series([keyword,d1,headline,time,cont,link], index=df1.columns)
            df1 = df1.append(new_column,ignore_index=True)
            #store 
            new_column1 = pd.Series([keyword,d1,headline,time,cont,link], index=df2.columns)
            df2 = df2.append(new_column1,ignore_index=True)

        df1.to_csv('thai_news.csv')
        df2.to_csv('store_thai_news.csv', mode = 'a',header= ['Keyword','Date','Headline','Posted', 'Content', 'Link'] , encoding='utf-8',index= True)
        

        df = pd.read_csv('thai_news.csv')
        self.textnews.clear() #clear old news
        for i in df['Headline'].unique():
            self.textnews.append('-'+i+'\n') #add news in textbrowser

        # plot pie chart
        self.thai_sent('thai_news.csv')

    #thai sentiment
    def thai_sent(self,path):
        
        df = pd.read_csv(path)
        
        P = self.loadData() #pickle เรียกไฟล์โหลดมา
        pos = 0
        neg = 0
        neu = 0
        for news in df['Headline']:

            sentence = news
            featurized_test_sentence =  {i:(i in self.clean_thai(sentence.lower())) for i in P[1]}
                
            #ทำการ train โมเดลด้วยอัลกอริทึม Naive Bayes โดยใช้ NLTK
            if P[0].classify(featurized_test_sentence) == 'pos':
                pos += 1
            elif P[0].classify(featurized_test_sentence) == 'neg':
                neg += 1
            else:
                neu += 1

        print('Thai-News Sentiment')
        print("Total Positive : ", pos)
        print("Total Negative : ", neg)
        print("Total Neutral :", neu)


        labels = ['positive','negative','neutral']
        sizes =  [pos,neg,neu]
        explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90 , colors=['green', 'red', 'yellow'])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Thai-News Sentiment')
        plt.savefig('C:/software/software2/pic/thnews_sent.png')
        self.sent_news.setStyleSheet('border-image: url(C:/software/software2/pic/thnews_sent.png);')

##--------------------find Th/Eng news-------------------------------------##
    def find_news(self,search) :
  
        if search == '': #ไม่มีให้เสิร์ชหา
            print('No News Update')

        elif re.match('[ก-๙]',search) !=  None: #เทียบภาษา
            self.get_thai_news(search)

        else :
            self.get_the_news(search)
                
###------------------------stock------------------------------------------###

    def search_stock(self,search,s,e):   #ดึงข้อมูลราคาหุ้น จาก https://finance.yahoo.com/portfolios

        if search == '' :  #ไม่มีหุ้น     
            print('no search stock')

        elif search != '' : #หาหุ้น
            df = data.DataReader(search,data_source='yahoo',start = s,end = e)
            df.to_csv('stock.csv')

            #plot graph
            self.plot_stock('stock.csv',search)
            plt.close('all') #closes all the figure windows
        
    def plot_stock(self,path,name): #https://saralgyaan.com/posts/python-candlestick-chart-matplotlib-tutorial-chapter-11/
        #abroad stock ex fb,amzn,aapl,goog,msft, TSLA
        #crypto ex XRP-USD , BTC-USD ,XLM-USD,ADA-USD,DOT1-USD,DOGE-USD
        #thai stock ex PTT.BK,AOT.BK,SCC.BK,KTB.BK,SCB.BK,CPALL.BK,OR.BK
        #ชื่อย่อหุ้นไทยจะมีชื่อ .BK ตามหลังชื่อย่อหุ้น
        plt.style.use('ggplot')
        data = pd.read_csv(path)
    
        ohlc = data.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
        ohlc['Date'] = pd.to_datetime(ohlc['Date'])
        ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
        ohlc = ohlc.astype(float)

        # Creating Subplots
        fig, ax = plt.subplots()
        candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

        # Setting labels & titles
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Formatting Date
        date_format = mpl_dates.DateFormatter('%d-%m-%Y')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()

        fig.tight_layout()

        ohlc['SMA5'] = ohlc['Close'].rolling(5).mean()
        ax.plot(ohlc['Date'], ohlc['SMA5'], color='green', label='SMA5')
        #เส้น SMA ย่อมาจากคำว่า Simple Moving Average ซึ่งเป็นการหาค่าเฉลี่ยอย่างง่าย 
        #ปกติแล้วเส้น SMA นิยมนำมาใช้มองหาแนวโน้มของราคา และยังช่วยมองหาเส้นแนวรับราคา หรือแนวต้านราคาไปในตัวด้วย

        fig.suptitle(name +' with SMA5')

        plt.legend()

        plt.savefig('C:/software/software2/pic/stock.jpg')
        self.graph.setStyleSheet('border-image: url(C:/software/software2/pic/stock.jpg);')

#-------------เรียกใช้งานโปรแกรม--------------------------#
app = QApplication(sys.argv)
myWindow = MyWindowClass()
app.exec_()