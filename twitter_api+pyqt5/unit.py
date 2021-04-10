from testapi import * 
import unittest

#ถ้าจะตรวจสอบอะไร ต้อง return
#twit,news,stock,date1,date2
work = Worker('โควิด19','','','16/03/2021','18/04/2021') 

class Unit_test(unittest.TestCase):
    def test(self):
        #t1 = work.twit() #twitter
        #t2 = work.find_news() #web crawler
        #t3 = work.check_news()
        t4 = work.search_part1()
        #t5 = work.search_stock() #stock
#------------------Tester-----------------------------#
        self.assertTrue(t4) # when value is true

if __name__ == '__main__':
    unittest.main()


