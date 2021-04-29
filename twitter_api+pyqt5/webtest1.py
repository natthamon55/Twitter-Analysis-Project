import requests
from bs4 import BeautifulSoup, SoupStrainer
import csv
import re
import time
from datetime import datetime
from datetime import timedelta
import pandas
import concurrent.futures

class websites_crawler:
    def __init__(self):
        self.max_thread = 10

        self.en_url = []
        self.th_url = []

        self.domain_en = []
        self.domain_th = []
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.name_link = open('web_crawler.csv', 'w', newline='', encoding='utf-8')
        #fieldnames = ['thai', 'global']
        fieldnames = ['All']
        self.news_writer = csv.DictWriter( self.name_link, fieldnames = fieldnames )
        self.news_writer.writeheader()
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        name_file = "web_" + datetime.now().strftime("%Y-%m-%d") + "_.csv"
        self.each_file = open( name_file , 'a', newline='', encoding='utf-8')
        fieldnames_2 = ['head_news', 'link', 'content','time','main_link']
        self.writer = csv.DictWriter( self.each_file, fieldnames = fieldnames_2 )
        self.writer.writeheader()
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        url_all_link = open("100_Link.txt", "r")
        all_url = []

        for lib in url_all_link:
            all_url.append(lib.split("\n")[0])

        self.main_url = all_url

        for news in all_url :
            self.news_writer.writerow( { 'All': news } )

        self.name_link.close()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        for link in all_url :
            self.domain_th.append(link.split("/")[2])

        self.domain = self.domain_th

        set_pattern = {("meta","property","og:type"):3, ("meta","name","og:type"):2, ("meta","property","og:url"):1, ("meta","name","og:url"):0} 
        self.pattern_list = sorted(set_pattern, key=set_pattern.get, reverse=True)

        self.output = []


    def main(self) :

        t0 = time.time()
        self.concurrent_futures(self.download_url, self.main_url, self.domain, ['run']*len(self.main_url))
        self.each_file.close()
        t1 = time.time()

        print(f"time: {t1-t0} seconds, length: {len(self.output)} links.")


    def concurrent_futures(self, func, arg1, arg2, arg3):
        threads = min(self.max_thread, len(arg1))

        if threads <= 0 :
            threads += 1
            
        r = None
        with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
            for i in executor.map(func, arg1, arg2, arg3):
                r = i
        return r


    def download_url(self, url, domain, no_use):
        try:
            print(str(self.domain.index(domain)//self.max_thread)+"_A")
            #self.check_bug.write(str(self.DOMAIN_en.index(domain)//self.MAX_THREADS)+"_A"+"\n")
            #self.check_bug.flush()
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, "html.parser")
            stories = soup.find_all("a")

            links = []
            for http in stories:
                if http["href"] :
                    temp = self.link_format(http["href"], domain)
                    links.append(temp)

            topic = self.find_topic(resp.content, domain)
            t0 = time.time()

            self.concurrent_futures(self.check_type, links, [url]*len(links), [topic]*len(links))

            t1 = time.time()
            print(t1-t0, "end thread")

            #self.check_bug.write(str(t1-t0)+"\n")
        except KeyError:
            pass
        return 1

    def check_type(self, link, domain, topic):
        poor_domain = domain.split("/")[2]
        if link not in topic :
            try: 
                print(str(self.domain.index(poor_domain)//self.max_thread)+"_B")
                #self.check_bug.write(str(self.DOMAIN_en.index(domain)//self.MAX_THREADS)+"_B"+"\n")
                #self.check_bug.flush()
                res = requests.get(link, timeout=20)
                html_page = res.content
                soup = BeautifulSoup(html_page, "html.parser")

                type_ = None
                for pattern in self.pattern_list:
                    type_ = soup.find(pattern[0], {pattern[1]:pattern[2]})
                    if(type_ != None):
                        break

                try :
                    if(type_["content"] == ""):
                        # og:type is empty string
                        return "website"
                    elif(type_["content"] == link):
                        # has same link in og:url meta tags
                        self.output.append(link)
                        self.find_message(link, html_page, domain)
                        return "article"
                except TypeError :
                    pass
                    
                if type_ :
                    x = type_["content"]
                    if(x == "article"):
                        self.output.append(link)
                        self.find_message(link, html_page, domain)
                    return x
                else:
                    return "No meta type"

            # --------------------- it's not a real link ---------------------
            except requests.exceptions.MissingSchema:
                print("MissingSchema",link)
                return "No"
            except requests.exceptions.InvalidSchema:
                print("InvalidSchema",link)
                return "No"
            except requests.exceptions.SSLError:
                print("SSLError",link)
                return "No"
            except requests.exceptions.ConnectionError:
                print("ConnectionError",link)
                return "No"
            except requests.exceptions.ReadTimeout:
                print("ReadTimeout",link)
                return "No"
            except requests.exceptions.TooManyRedirects:
                print("TooManyRedirects",link)
                return "No"
            except requests.exceptions.InvalidSchema:
                print("InvalidSchema",link)
                return "No"
            except requests.exceptions.ChunkedEncodingError:
                print("ChunkedEncodingError",link)
                return "No"
            # ----------------------------------------------------------------

    def link_format(self, str_input, domain):

        # if it's empty string str_out set to empty string it's mean it's not link
        if(str_input == ""):
            str_out = ""
        else:
            str_out = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", str_input)

            # if str_out is None go to forming link to correct full link
            if(str_out == None):
                if( str_input[0:2] == "//" and len(str_input) > 3 ):
                    str_out = "https:"+str_input
                elif(str_input[0] == "/" and len(str_input) > 3):
                    str_out = "https://"+domain+str_input
                elif(str_input[0:2] == "./" and len(str_input) > 3):
                    str_out = "https://"+domain+"/"+str_input[2:]
                    #print(str_out)
                else:
                    str_out = ""
            else:
                # if str_out isn't None it's mean str_out is a link can be search
                str_out = str_out.group()
                # but some values of str_out isn't exist https:// or http://
                if("https://" in str_out or "http://" in str_out):
                    pass
                else:
                    str_out = "https://"+str_out
            
        return str(str_out)


    def find_message(self, url, html_page, main_link) :

        soup = BeautifulSoup(html_page, 'html.parser', parse_only=SoupStrainer("div"))
        he = BeautifulSoup(html_page, 'html.parser')

        title = he.find("meta",  property="og:title") 
        title = title["content"] if title else "" 

        message = soup.find_all(name="p")

        complete_content = ""
        output = []

        for i in message:
            complete_content += i.text + "\n"

        time = self.find_time(html_page)

        check_double = []
        if time[0] == datetime.now().strftime("%Y-%m-%d") :
            back_up = self.file_manage("web_" + datetime.now().strftime("%Y-%m-%d") + "_.csv")
            try:
                if (url not in check_double) and (url not in back_up) :
                    self.writer.writerow( { 'head_news': str(title), 'link': url, 'content': complete_content, 'time': time[0] + " " + time[1], 'main_link': main_link } )
                    check_double.append( url )
                    print('oh yes')

            except TypeError:
                print('oh no')
        else :
            back_up = self.file_manage("web_" + time[0] + "_.csv")
            try:
                if (url not in check_double) and (url not in back_up) :

                    name_file = "web_" + time[0] + "_.csv"
                    each_file = open( name_file , 'a', newline='', encoding='utf-8')
                    fieldnames = ['head_news', 'link', 'content','time','main_link']
                    writer = csv.DictWriter( each_file, fieldnames = fieldnames )
                    writer.writeheader()
                    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                    writer.writerow( { 'head_news': str(title), 'link': url, 'content': complete_content, 'time': time[0] + " " + time[1], 'main_link': main_link } )
                    check_double.append( url )
                    each_file.close()
                    print('oh yes 2.0')

            except TypeError:
                print('oh no 2.0')

    def find_time(self, html_page) :

        # find time from website
        try:
            soup = BeautifulSoup(html_page, 'html.parser', parse_only=SoupStrainer("script"))
            date = soup.find_all(name="script")

            reg = re.compile(r'(?P<date>202\d-\d\d-\d\d)(?P<time>T\d\d:\d\d:\d\d| \d\d:\d\d)')
            ou = reg.search(str(date))
            date_output = ou.group("date")
            time_output = ou.group("time")[1:]

            return [str(date_output), str(time_output)]
        except AttributeError:
            # Ex:: Jan 27 2021 06:31:00:000PM+07:00 ==> 2021-01-27 18:31:00
            try:
                reg = re.compile(r'(?P<date>\w\w\w \d\d \d\d\d\d)(?P<time> \d\d:\d\d:\d\d:000AM| \d\d:\d\d:\d\d:000PM)')
                ou = reg.search(str(date))
                date_output = ou.group("date")
                time_output = ou.group("time")[1:]

                temp1=datetime.strptime(date_output,"%b %d %Y")
                temp2=datetime.strptime(time_output,"%I:%M:%S:000%p")

                return [str(temp1).split(" ")[0], str(temp2).split(" ")[1]]
            except AttributeError:
                # it isn't Jan 27 2021 06:31:00:000PM+07:00 
                date_now = str(datetime.now()).split(" ")
                reg = re.compile(r'(?P<date>202\d-\d\d-\d\d)(?P<time> \d\d:\d\d:\d\d)')
                ou = reg.search(str(datetime.now()))
                date_output = ou.group("date")
                time_output = ou.group("time")[1:]
                
                return [str(date_output), str(time_output)]

    def find_topic(self, html_page, domain) :

        try:
            set_html_tag = ["nav", "header", "div"]
            data = []
            count = 0
            # -------------------------------------- header --------------------------------------
            while( data == [] and (count != len(set_html_tag)) ) :
                soup = BeautifulSoup(html_page, 'html.parser', parse_only=SoupStrainer(set_html_tag[count]))
                data = soup.find_all(name="ul")
                count += 1
            storage = []
            for i in data:
                temp = i.find_all("li")
                for j in temp:
                    try:
                        g = j.find("a")["href"]
                        g = self.link_format(g, domain)
                        if(g == ""):
                            continue
                        storage.append(g)
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            # -------------------------------------------------------------------------------------

            # -------------------------------------- tail --------------------------------------
            soup1 = BeautifulSoup(html_page, 'html.parser', parse_only=SoupStrainer("footer"))
            sub_footer = []
            for i in soup1.find_all("a"):
                if(i.get("href") == None):
                    continue
                footer = self.link_format(i.get("href"), domain)
                if(footer == ""):
                    continue
                sub_footer.append(footer)

            return storage+["*"*10]+sub_footer
        except requests.exceptions.ReadTimeout:
            return []
        except requests.exceptions.TooManyRedirects:
            return []
            # ---------------------------------------------------------------------------------

    def check_domain(self, link, domain):
        link = self.link_format(link, domain)
        link = link.split("/")[2]

        if(link != domain):
            return False
        return True


    def file_manage(self,keyword) :
        output = []
        try :
            load = pandas.read_csv(keyword)
            for data in load['link'] :
                output.append(data)
            return output

        except FileNotFoundError :
            return output
        except pandas.errors.EmptyDataError :
            return output
#_________________________________________________________________________________________________________________________________________________________

if __name__ == "__main__":
    obj = websites_crawler()
    obj.main()