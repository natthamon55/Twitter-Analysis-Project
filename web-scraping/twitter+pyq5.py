#ref : https://pbj0812.tistory.com/198
#ref  : https://www.kaggle.com/drvaibhavkumar/twitter-data-analysis-using-tweepy
#ref : https://medium.com/botnoi-classroom/%E0%B8%A5%E0%B8%AD%E0%B8%87%E0%B8%A7%E0%B8%B4%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%B0%E0%B8%AB%E0%B9%8C%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5-twitter-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%AA%E0%B9%84%E0%B8%95%E0%B8%A5%E0%B9%8C%E0%B9%82%E0%B8%AD%E0%B8%95%E0%B8%B0-bnk-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-tweepy-pandas-%E0%B9%81%E0%B8%A5%E0%B8%B0-nlp-part-1-e454aeff443a
# Mini Project : Twitter Api Search (6201012620139)

import sys  
from PyQt5.QtWidgets import *  #สร้าง pyqt5 สำหรับ gui
import tweepy #ใช้ดึงข้อมูลจากทวิตเตอร์
import pandas as pd  #ใช้ในการสร้าง dataframe
import matplotlib.pyplot as plt #ใช้ในการplot pie chart 
from textblob import TextBlob  #ใช้สำหรับประมวลผลข้อมูลที่เป็นข้อความ Sentiment Analysis

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
        
        self.btn = QPushButton('Search')
        self.btn.clicked.connect(self.twit)
        
        grid = QGridLayout()
        grid.addWidget(self.le, 0, 0, 1, 4)      
        grid.addWidget(self.btn, 2, 0, 1, 4)

        self.setLayout(grid)

        self.setWindowTitle('Twitter Api Search')
        self.setGeometry(100, 100, 400, 250)
        self.show()

    #-----------------------------------------------------------------------------#
    def twit(self):

        #Getting authorization
        consumer_key = '*************'
        consumer_secret = '**************'
        access_token = '***********************'
        access_token_secret = '*********************'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #การอนุญาติเข้าถึง api
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        keyword = self.le.text()
        max_tweets = 100
        search_tweets = [status for status in tweepy.Cursor(api.search, q=keyword).items(max_tweets)]

        # sentiment analysis (+ - 0)
        pos = 0
        neg = 0
        inde = 0
        for tweet in search_tweets:
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
        df = pd.DataFrame(columns= ['create_at', 'text', 'hashtag', 'retweet_count', 'favourite_count'])
        for tweet in search_tweets :
            
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ' '
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'# '+entity_hashtag[i]['text']
            
            create_at = tweet.created_at
            re_count = tweet.retweet_count
            fav_count = tweet.favorite_count

            new_column = pd.Series([create_at,tweet.text,hashtag,re_count,fav_count], index=df.columns)
            df = df.append(new_column,ignore_index=True)
        
        df.to_excel('./twitter_result.xlsx') #แปลงเป็น ไฟล์ตารางใน excel 

#----------------------------------------------------------------------#    
             
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
