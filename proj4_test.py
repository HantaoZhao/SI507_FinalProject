import unittest
from proj4 import *

class TestProj4(unittest.TestCase):
    def test01(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT EnglishName
            FROM Countries
            WHERE Region="Oceania"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Australia',), result_list)
        self.assertIn(('New Zealand',), result_list)
        self.assertEqual(len(result_list), 27)

        sql = '''
            SELECT EnglishName
            FROM Countries
            WHERE Region="Asia"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Iran',), result_list)
        self.assertIn(('Japan',), result_list)
        self.assertEqual(len(result_list), 50)

    def test02(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT COUNT(*)
            FROM Countries
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 250 or count == 251)

        sql = '''
            SELECT COUNT(*)
            FROM Weather
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count>100,True)

        conn.close()

    def test03(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT (SELECT EnglishName FROM Countries WHERE Id=CountryId)
            FROM Weather
            WHERE CityName="Algiers"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Algeria',), result_list)
        self.assertEqual(len(result_list), 1)

        sql = '''
            SELECT (SELECT EnglishName FROM Countries WHERE Id=CountryId)
            FROM Weather
            WHERE CityName="Beijing"
        '''

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('China',), result_list)
        self.assertEqual(len(result_list), 1)

        sql = '''
            SELECT (SELECT EnglishName FROM Countries WHERE Id=CountryId)
            FROM Weather
            WHERE CityName="Athens"
        '''

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Greece',), result_list)
        self.assertEqual(len(result_list), 1)


        conn.close()

    def test04(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT * FROM Weather
        '''

        results = cur.execute(sql)
        temp=[]
        for i in cur:
            temp=i
            break

        # print(temp)
        self.assertEqual(len(temp), 8)

        sql = '''
            SELECT * FROM Countries
        '''

        results = cur.execute(sql)
        temp=[]
        for i in cur:
            temp=i
            break

        self.assertEqual(len(temp), 8)

        conn.close()



unittest.main(verbosity=2)
