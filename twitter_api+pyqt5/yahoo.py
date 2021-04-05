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