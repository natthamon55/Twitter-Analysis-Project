#twitter api data analysis
#ref :https://www.youtube.com/watch?v=HDjc3w1W9oA
#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
#qt design( .ui file) + open csv + word_cloud(nlp with thai and english) + sentiment analysis

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget,QTableWidget, QTableWidgetItem
from PyQt5 import uic
import sys
import os
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis
from wordcloud import WordCloud #ใช้แสดงผลกลุ่มคำที่เจอบ่อย
import re #ลบ pattern ของคำที่ไม่ต้องการออกด้วย
import emoji
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
        self.btnsent.clicked.connect(self.emotion) #sentiment analysis
        self.btnword.clicked.connect(self.w_cloud) #wordcloud
        self.btnopen.clicked.connect(self.OpenFile) #open csv
        self.btnshow.clicked.connect(self.dataHead) #show csv

    def twit(self):
        #Getting authorization
        self.consumer_key = ''
        self.consumer_secret = ''
        self.access_token = ''
        self.access_token_secret = ''

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret) #การอนุญาติเข้าถึง api
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

        self.keyword = self.lineEdit.text()
        self.language = self.comboBox.currentText()
        self.max_tweet = int(self.lineEdit_2.text())

        self.search_tweet1 = [status for status in tweepy.Cursor(self.api.search, q=self.keyword,lang=self.language).items(self.max_tweet)]
        #ตั้งค่าให้รับข้อมูลล่าสุดของทวิตและรับข้อความแบบไม่มีการตัด
        self.search_tweet2 = tweepy.Cursor(self.api.search,q=self.keyword,lang=self.language,result_type='recent',tweet_mode='extended').items(self.max_tweet)
        #create dataframe use pandas 

        self.df = pd.DataFrame(columns= ['create_at', 'text', 'hashtag', 'retweet_count', 'favourite_count']) #สร้างตาราง

        for tweet in self.search_tweet2 :
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ' '
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'# '+entity_hashtag[i]['text']

            create_at = tweet.created_at #เวลา
            re_count = tweet.retweet_count #จน รีทวิต

            #หากเจอข้อความในหัวข้อ retweet ให้ใช้ข้อความและจำนวนผู้กด Favourite จากทวิตดั่งเดิม แต่หากไม่พบให้ดึงข้อมูลจากทวิตอันนั้นได้เลย
            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            self.new_column = pd.Series([create_at,text,hashtag,re_count,fav_count], index=self.df.columns)
            self.df = self.df.append(self.new_column,ignore_index=True)
            self.df.sort_values(by=['retweet_count','favourite_count'], inplace=True,ascending=False) #เรียงจากมาก-->น้อย
        
        
        self.df.to_excel('twitter.xlsx') #แปลงเป็น ไฟล์ตารางใน excel
        self.df.to_csv('twitter.csv')  #แปลงเป็น csv ไฟล์

        #show data
        data1 = self.df.drop_duplicates("text").sort_values(by=['retweet_count'], ascending=False).head(10)[['text','retweet_count']]
        print(f'Top 10 Tweet in Twitter : {self.keyword}')
        print(data1)
        print('-------------------------------------------------------------------------------------------------------------------------------')


    def emotion(self):
        # sentiment analysis (+ - 0)
        pos = 0
        neg = 0
        inde = 0
        for tweet in self.search_tweet1:
            analysis = TextBlob(tweet.text)
            if analysis.sentiment[0]>0:  #1 is positive
                pos +=  1
            elif analysis.sentiment[0]<0: #-1 is a negative
                neg +=  1
            else:   # 0 is independent  
                inde +=  1

        print(f"Total Positive =>   {pos}")
        print(f"Total Negative =>   {neg} ")
        print(f"Total Independent =>   {inde}")
        print('-------------------------------------------------------------------------------')

        #Plot pie use matplotlib.pyplot
        labels = 'Positive + ', 'Negative - ', 'Independent 0 '
        sizes = [pos, neg, inde]
        colors = ['gold', 'yellowgreen', 'lightcoral']
        explode = (0.1, 0, 0) 
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.show()

    
    def w_cloud(self):

        word =[]
        t = self.df['text'] #ข้อความทวิตในตาราง

        for item in t :

            if re.match('[ก-๙]',item) !=  None:

                for i in range(0,self.max_tweet):

                    text = self.df['text'][i]
                    text = re.sub(r'https?:\/\/.*[\r\n]', '', text,flags=re.MULTILINE) # ลบ pattern ของคำที่ไม่ต้องการออก
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
                    tweet = re.sub('[a-z A-Z ]', '', text)
                    stop_word = list(thai_stopwords()) #มาจาก pythainlp 
                    sentence = word_tokenize(tweet,engine='newmm') #การตัดคำให้ออกมาเป็น list
                    result = [word for word in sentence if  word not in stop_word and " " not in word]
                    tweet = ' '.join(result)
                    word.append(tweet)

            else :

                for i in range(0,self.max_tweet):
                    
                    text = self.df['text'][i]
                    text = re.sub('[^a-zA-Z0-9]', ' ', text)
                    text = re.sub(r'https?:\/\/.*[\r\n]', '', text,flags=re.MULTILINE) # ลบ pattern ของคำที่ไม่ต้องการออก
                    allchars = [str for str in text]
                    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI] #ลบ emoji ออก
                    text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
                    text = text.lower()
                    text = text.split()
                    ps = PorterStemmer()
                    result = [ps.stem(word) for word in text if not word in set(stopwords.words('english'))]
                    tweet = ' '.join(result)
                    word.append(tweet)


        #print(word)

        #wordcloud
        all_words = ' '.join([text for text in word])
        regexp = r"[ก-๙a-zA-Z']+"
        path = 'C:\software\software2\THSarabunNew.ttf'
        wordcloud = WordCloud(font_path=path,background_color="white",max_words=200,width=1024, height=768, random_state=21, max_font_size=100,regexp=regexp).generate(all_words)
        plt.figure(figsize=(10, 7))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis('off')
        plt.show()


    def OpenFile(self):

        try:
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')[0]
            self.all_data = pd.read_csv(path)
        except:
            print(path)

    def dataHead(self):

        numColomn = self.spinBox.value()
        if numColomn == 0:
            NumRows = len(self.all_data.index)
        else:
            NumRows = numColomn
        self.tableWidget.setColumnCount(len(self.all_data.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(self.all_data.columns)

        for i in range(NumRows):
            for j in range(len(self.all_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.all_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()


#-------------เรียกใช้งานโปรแกรม--------------------------#
app = QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
