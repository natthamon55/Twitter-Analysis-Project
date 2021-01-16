#Ref : -https://www.youtube.com/watch?v=X2EpWtIYIjY
# -https://medium.com/@rithikied/%E0%B8%A3%E0%B8%B9%E0%B9%89%E0%B8%88%E0%B8%B1%E0%B8%81%E0%B8%84%E0%B8%A3%E0%B9%88%E0%B8%B2%E0%B8%A7%E0%B9%86-%E0%B8%82%E0%B8%AD%E0%B8%87-%E0%B9%84%E0%B8%AD%E0%B9%89-beautiful-soup-4-417404c69da

import requests #เครื่องมือดึงข้อมูลจาก website
from bs4 import BeautifulSoup #สำหรับดึงข้อมูลหน้าเว็บ หรือ HTML
import time 

def getweb():

    search = input("search : ")
    web = 'https://www.foxnews.com/'
    data = requests.get(web) #ดึงข้อมูลทั้งหมดจากหน้าเว็บ

    soup =  BeautifulSoup(data.text ,'html.parser') #parser แปลงภาษาตัดเครื่องหมายที่ไม่ต้องการออกไป 
    f_title = soup.find_all('h2',{'class': 'title title-color-default'}) #ค้นหาว่าจะดึงส่วนไหนมาแสดงจากเว็บไซต์

    for i in f_title : #เพื่อแสดงหัวข้อข่าว

        i = str(i).split('<h2 class="title title-color-default">') #แบ่งคำ โดยเมื่อแบ่งจะได้ข้อมูล เป็น list ออกมา
        i = str(i).split('</h2>')[0] 
        i = str(i).split('</a>') [0]

        if str(search) == 'all' or str(search) == ' ':
            print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(i)

        elif str(search) in i :
            print(i)

    time.sleep(10) #แบบ Real-Time ทุกๆ 10 วิ
    getweb()

getweb()
