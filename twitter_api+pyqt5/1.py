#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
# Mini Project : Twitter Api Search (6201012620139)
#twitter api + pyqt5 + sentiment analysis + wordcloud (english) + excel

import sys  
from PyQt5.QtWidgets import *  #สร้าง pyqt5 สำหรับ gui
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis
from wordcloud import WordCloud #ใช้แสดงผลกลุ่มคำที่เจอบ่อย
import re #ลบ pattern ของคำที่ไม่ต้องการออกด้วย
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

class MyApp(QWidget):   
    # pyqt5 gui
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        lbl1 = QLabel('Tweepy_Twit:) ', self)
        lbl1.move(150, 20)

        self.le = QLineEdit()
        self.le.setPlaceholderText('Enter your search word')
        self.le.returnPressed.connect(self.twit)

        self.le2 = QLineEdit()
        self.le2.setPlaceholderText('How many tweet to analyze ')
        self.le2.returnPressed.connect(self.twit)
        
        self.btn = QPushButton('Search')
        self.btn.clicked.connect(self.twit)
        
        grid = QGridLayout()
        grid.addWidget(self.le, 1, 0, 1, 2)
        grid.addWidget(self.le2, 2, 0, 1, 2)
        grid.addWidget(self.btn, 3, 0, 1, 2)

        self.setLayout(grid)

        self.setWindowTitle('Twitter Api Search')
        self.setStyleSheet("background-color: rgb(153,255,255)")
        self.setGeometry(0, 0, 400, 300)
        self.show()

    #-----------------------------------------------------------------------------#
    def twit(self):

        #Getting authorization
        consumer_key = ' '
        consumer_secret = ' '
        access_token = ' '
        access_token_secret = ' '

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #การอนุญาติเข้าถึง api
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        keyword = self.le.text()
        max_tweet = int(self.le2.text())
        search_tweet1 = [status for status in tweepy.Cursor(api.search, q=keyword).items(max_tweet)]
        search_tweet2 = tweepy.Cursor(api.search,q=keyword,result_type='recent',tweet_mode='extended').items(max_tweet)

        # sentiment analysis (+ - 0)
        pos = 0
        neg = 0
        inde = 0
        for tweet in search_tweet1:
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

        #Plot pie use matplotlib.pyplot
        labels = 'Positive + ', 'Negative - ', 'Independent 0 '
        sizes = [pos, neg, inde]
        colors = ['gold', 'yellowgreen', 'lightcoral']
        explode = (0.1, 0, 0)  
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.show()

        
        #create dataframe use pandas 
        df = pd.DataFrame(columns= ['create_at', 'text', 'hashtag', 'retweet_count', 'favourite_count']) #สร้างตาราง

        for tweet in search_tweet2 :
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ' '
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'# '+entity_hashtag[i]['text']

            create_at = tweet.created_at #เวลา
            re_count = tweet.retweet_count #จน รีทวิต

            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            new_column = pd.Series([create_at,text,hashtag,re_count,fav_count], index=df.columns)
            df = df.append(new_column,ignore_index=True)
        
        #แปลงเป็น ไฟล์ตารางใน excel
        df.to_excel('twitter_result.xlsx') #แปลงเป็น ไฟล์ตารางใน excel

        #Word Cloud
        corpus = []
        for i in range(0, 100):
            tweet = re.sub('[^a-zA-Z0-9]', ' ', df['text'][i])
            tweet = tweet.lower()
            tweet = re.sub('rt', '', tweet)
            tweet = re.sub('http', '', tweet) #การเขียนทับข้อความตรงส่วนนั้นๆด้วย ' ' เหมือนกับการลบออก
            tweet = re.sub('https', '', tweet)
            tweet = tweet.split() #ลบข้อมูลตรงส่วนนั้นออก และตัดข้อความออกจากกัน
            ps = PorterStemmer() #เป็นอัลกอริทึมที่จะช่วยตัดคำออกเป็นคำๆ
            tweet = [ps.stem(word) for word in tweet if not word in set(stopwords.words('english'))]
            tweet = ' '.join(tweet)
            corpus.append(tweet)
        
        #Word Cloud แสดงผลกลุ่มคำโดยคำที่มีจำนวนมากสุดจะมีขนาดใหญ่สุด
        all_words = ' '.join([text for text in corpus])
        wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)
        plt.figure(figsize=(10, 7))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis('off')
        plt.show()

#----------------------------------------------------------------------#    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
