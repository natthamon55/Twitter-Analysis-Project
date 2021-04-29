from testapi import * 
import unittest
#ถ้าจะตรวจสอบอะไร ต้อง return true
#twit,news,stock,date1,date2

#work = Worker('covid','','','11/03/2021','19/04/2021') 
#work = Worker('','','btc-usd','11/03/2021','19/04/2021')
work = Worker('','covid','','24/04/2021','29/04/2021')
#work = Worker('bitcoin','bitcoin','btc-usd','11/03/2021','19/04/2021')

class Unit_test(unittest.TestCase):
    def test(self):
        #t1 = work.twit() #twitter
        #t3 = work.check_news()
        t4 = work.search_part1()
        #t5 = work.search_stock() #stock
#------------------Tester-----------------------------#
        self.assertTrue(t4) # when value is true

if __name__ == '__main__':
    unittest.main()


