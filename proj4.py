import requests
import json
import sqlite3
import plotly.graph_objects as go
import plotly.offline as of
from flask import Flask, render_template
from bs4 import BeautifulSoup

DBNAME = 'proj4.db'
COUNTRIESJSON = 'countries.json'
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()
# of.offline.init_notebook_mode(connected=True)

app = Flask(__name__)

# class City():
#     def __init__(self,CityName,Temperature,Weather,Feel,Forecast,Wind,Humidity,CountryId,CountryName):
#         self.name=CityName
#         self.tem=Temperature
#         self.wea=Weather
#         self.feel=Feel
#         self.fore=Forecast
#         self.wind=Wind
#         self.hum=Humidity
#         self.id=CountryId
#         self.country=CountryName
#
#     def __str__(self):
#         pass

class City():
    def __init__(self,tup):
        self.name=tup[0]
        self.tem=tup[1]
        self.wea=tup[2]
        self.feel=tup[3]
        self.fore=tup[4]
        self.wind=tup[5]
        self.hum=tup[6]
        self.id=tup[7]
        self.country=tup[8]

    def __str__(self):
        temp = '\n'+self.name+' is in '+self.country
        temp += '\nIts temperature in the next six hours are: '+'°F '.join(self.tem.split('°F'))
        temp += '\n\tThe weather today is: '+self.wea
        temp += '\n\tIt feels like: '+self.feel
        temp += '\n\tThe high and low forecast temperature today is: '+self.fore
        temp += '\n\tThe wind now is: '+self.wind
        temp += '\n\tThe humidity is: '+self.hum
        return temp

def db_init():
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute("DROP TABLE IF EXISTS 'Weather'")
    cur.execute("DROP TABLE IF EXISTS 'Countries'")

    statement = """
    CREATE TABLE `Countries` (
            `Id`            INTEGER PRIMARY KEY AUTOINCREMENT,
            `Alpha2`        TEXT NOT NULL,
            `Alpha3`        TEXT NOT NULL,
            `EnglishName`   TEXT NOT NULL,
            `Region`        TEXT,
            `Subregion`     TEXT,
            `Population`    Integer,
            `Area`          Real
    );
    """

    cur.execute(statement)

    with open(COUNTRIESJSON, 'rb') as f:
        data = json.load(f, encoding='utf-8')

    for i in data:
        cur.execute(
            "INSERT INTO 'Countries'(Alpha2,Alpha3,EnglishName,Region,Subregion,Population,Area) VALUES(?,?,?,?,?,?,?)",
            (i['alpha2Code'], i['alpha3Code'], i['name'], i['region'], i['subregion'], i['population'], i['area'])
        )

    statement="""
    CREATE TABLE `Weather`(
            `CityName`              TEXT PRIMARY KEY,
            `Temperature`           TEXT,
            `Weather`               TEXT,
            `Feel`                  TEXT,
            `Forecast`              TEXT,
            `Wind`                  TEXT,
            `Humidity`              TEXT,
            `CountryId`             Integer NULL,
            FOREIGN KEY(CountryId) REFERENCES Countries(Id)
    );
    """

    cur.execute(statement)

# scraping and caching
CACHE_FNAME = 'cache.json'
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def get_unique_key(url):
  return url

def make_request_using_cache(url, header):
    unique_ident = get_unique_key(url)
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        # print("Making a request for new data...")
        resp = requests.get(url, headers=header)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def city_search(city_name,Country,City):
    #url="https://www.timeanddate.com/weather/usa/ann-arbor"

    CityName=City
    # print('CityName:',CityName)
    CountryName=Country
    # print('CountryName:',CountryName)

    cur.execute("select Id from Countries where EnglishName = \"" + CountryName + '\"')
    for i in cur:
        CountryId=i[0]
    # print('CountryId:',CountryId)

    url = "https://www.timeanddate.com"+city_name
    page=make_request_using_cache(url,header)
    # page_soup = BeautifulSoup(page.replace('<br ','<').replace('br',''), 'html.parser')
    page_soup = BeautifulSoup(page.replace('\xa0',''), 'html.parser')

    # temperature in next 6 hours
    tem = page_soup.find_all('tr',class_="h2")
    temperature=[]
    for i in tem:
        # print('')
        tds = i.find_all('td')
        for j in tds:
            # print(j.text)
            if "F" in j.text:
                temperature.append(j.text.replace('\xa0',''))

    Temperature=''.join(temperature)
    # print('Temperature:',Temperature)

    # print("\nWeather")
    weather = page_soup.find_all(id='cur-weather')
    for i in weather:
        Weather=i['title']

    # print('Weather:',Weather)

    # print("\nFeels like")
    feel=page_soup.find_all('p')
    for i in feel:
        if i.text.find('Feels Like')!=-1:
            Feel=i.text[12:i.text.find('Forecast')].replace('\0xa','')
            Forecast=i.text[i.text.find('Forecast')+10:i.text.find('Wind')].replace('\0xa','')
            Wind=i.text[i.text.find('Wind')+6:].replace(' ↑','')

    # print("Feel:",Feel)
    # print("Forecast:",Forecast)
    # print("Wind:",Wind)

    # print("\nConditions")
    conditions=page_soup.find_all("p")
    for i in conditions:
        if i.text.find('Wind') != -1:
            pass
        # elif i.text.find('Visibility:')!=-1:
        #     print(i.text)
        # elif i.text.find('Pressure:')!=-1:
        #     print(i.text)
        # elif i.text.find('Dew Point:')!=-1:
        #     print(i.text)
        elif i.text.find('Humidity:')!=-1:
            Humidity=i.text[i.text.find('Humidity:')+11:]
            # print("Humidity:",Humidity)

    cur.execute(
        "INSERT OR REPLACE INTO 'Weather'(CityName,Temperature,Weather,Feel,Forecast,Wind,Humidity,CountryId)  VALUES(?,?,?,?,?,?,?,?)",
        (CityName, Temperature, Weather, Feel, Forecast, Wind, Humidity, CountryId)
    )
    conn.commit()

    # print("\nForecast")
    # forecast=page_soup.find_all('span',title="High and low forecasted temperature today")
    # for i in forecast:
    #     print(i.text)


def city_init():
    url="https://www.timeanddate.com/weather/?sort=1"
    page=make_request_using_cache(url,header)
    page_soup = BeautifulSoup(page, 'html.parser')

    base_url="https://www.timeanddate.com"
    table=page_soup.find_all('tr')

    for i in table:
        temp=i.find_all('a')
        for j in temp:
            # print(base_url+j['href'])
            CountryName=j.text.split(', ')[0]
            CityName=j.text.split(', ')[-1]
            city_search(j['href'],CountryName,CityName)

def init():
    db_init()
    city_init()

# https://www.timeanddate.com/weather/results.html?query=ann+arbor
def add_city(cityname):
    baseurl="https://www.timeanddate.com/weather/results.html?query="
    page=make_request_using_cache(baseurl+cityname,header)
    page_soup = BeautifulSoup(page, 'html.parser')
    content=page_soup.find_all("td",class_="sep-thick")

    param=[]
    first_item=0
    for i in content:
        if first_item<=1:
            if i.find('a'):
                first_item+=1
                if first_item==1:
                    link=(i.find('a')['href'])
                elif first_item==2:
                    break
            param.append(i.text)

    city_search(link, param[-1], param[0])
    # print(param)
    # print(link)
    #

help="""
Commands available:

exit
    Terminate the program.

help
    Print the instructions for the program. 
    
all
    Print the weather conditions of every city in the database.

city <CityName>
    Show the weather conditions of a city. 
    The parameter <CityName> is required. For example: Ann Arbor, New York, Chicago, Washington DC

flask city <CityName>
    Show the weather conditions of a city. 
    The parameter <CityName> is required. For example: Ann Arbor, New York, Chicago, Washington DC
    Must rerun the program if flask is used.

country <CountryName>
    Show the weather conditions of cities in a country.
    The parameter <CountryName> is required. For example: USA, Canada, United Kingdom, Germany

region <RegionName>
    Show the weather conditions of cities in a region.
    The parameter <RegionName> is required. For example: Asia, Europe, Americas, Africa

"""


def commands():
    response=''
    print(help)
    while response!='exit':
        response=input('Please enter your command: ')
        response=response.lower()

        if response.find('help')!=-1:
            print(help)
        elif response.find('exit')!=-1:
            print('Goodbye!')
            break
        elif response.find('all')!=-1:
            # To check all the entries in the database
            cur.execute("SELECT *, (SELECT EnglishName FROM Countries WHERE Id=CountryId) AS CountryName FROM WEATHER")
            for i in cur:
                # print('para:',i)

                city=City(i)
                print(city)

        # cur.execute("SELECT CITYNAME, COUNT(CITYNAME), (SELECT EnglishName FROM Countries WHERE Id=CountryId) AS CountryName, Weather FROM WEATHER GROUP BY Weather")

        elif response.find('country')!=-1:
            country_name=response[response.find('country')+8:]
            # print('country_name:',country_name.strip().upper())
            # To group by Weather, and show the percentage by piechart
            cur.execute("SELECT COUNT(CITYNAME), Weather FROM WEATHER WHERE UPPER((SELECT EnglishName FROM Countries WHERE Id=CountryId)) = ? GROUP BY Weather",[country_name.strip().upper()])
            labels=[]
            values=[]
            for i in cur:
                # print(i)
                values.append(i[0])
                labels.append(i[1])

            # print(values)
            # print(labels)
            of.plot([go.Pie(labels=labels, values=values)])

            cur.execute(
                "SELECT CityName, Temperature FROM WEATHER WHERE UPPER((SELECT EnglishName FROM Countries WHERE Id=CountryId)) = ?", [country_name.strip().upper()])
            labels = []
            values = []
            for i in cur:
                # print(i)
                labels.append(i[0])
                values.append(i[1].split('°F'))

            # print(values)
            # print(labels)
            of.plot([go.Bar(x=labels, y=[i[0] for i in values])])

        elif response.find('region') != -1:
            region_name = response[response.find('region') + 7:]
            # print('region_name:', country_name.strip().upper())
            # To group by Weather, and show the percentage by piechart

            cur.execute(
                "SELECT COUNT(CITYNAME), Weather FROM WEATHER WHERE UPPER((SELECT Region FROM Countries WHERE Id=CountryId)) = ? GROUP BY Weather",[region_name.strip().upper()])
            labels = []
            values = []

            for i in cur:
                values.append(i[0])
                labels.append(i[1])

            # print(values)
            # print(labels)
            of.plot([go.Pie(labels=labels, values=values)])

            cur.execute(
                "SELECT CityName, Temperature FROM WEATHER WHERE UPPER((SELECT Region FROM Countries WHERE Id=CountryId)) = ?", [region_name.strip().upper()])

            labels = []
            values = []

            for i in cur:
                labels.append(i[0])
                values.append(i[1].split('°F'))

            of.plot([go.Bar(x=labels, y=[i[0] for i in values])])

        elif response.find('city')!=-1:
            # Line Chart of the temperature of a city
            cityname=response[response.find('city')+4:].strip()
            fl=(response.find('flask')!=-1)
            try:
                cur.execute("SELECT Temperature FROM Weather WHERE Upper(CityName)=?",[cityname.upper()])
                t=[]
                for i in cur:
                    t=i[0].split('°F')

                if t==[]:
                    raise RuntimeError

                # print(t)
                of.plot([go.Scatter(x=[0,1,2,3,4,5],y=t)])

                cur.execute("Select CityName, Temperature, Weather, Feel, Forecast, Wind, Humidity, CountryId, (SELECT EnglishName FROM Countries WHERE Id=CountryId) From Weather Where UPPER(CityName)=?",[cityname.upper()])
                res=[]
                for i in cur:
                    for j in i:
                        res.append(j)
                # print(res)

                if fl:
                    res[0]='City: '+res[0]
                    res[1]="The temperature in next 6 hours: "+'°F '.join(res[1].split("°F"))
                    res[2]="The weather is: "+res[2]
                    res[3]="It's feeling like: "+res[3]
                    res[4]='The high and low forecast temperature today is: '+res[4]
                    res[5]='The wind now is: '+res[5]
                    res[6]='The humidity is: '+res[6]
                    res[7]='It is in: '+res[-1]

                    @app.route('/')
                    def info():
                        return render_template('name.html',my_list=res)
                    # run()
                    app.run(use_reloader=False,debug=True)
                else:
                    c1=City(res)
                    print(c1)
            except:
                add_city(cityname)
                cur.execute("SELECT Temperature FROM Weather WHERE Upper(CityName)=?",[cityname.upper()])
                t=[]
                for i in cur:
                    t=i[0].split('°F')

                # print(t)
                of.plot([go.Scatter(x=[0,1,2,3,4,5],y=t)])

                cur.execute("Select CityName, Temperature, Weather, Feel, Forecast, Wind, Humidity, CountryId, (SELECT EnglishName FROM Countries WHERE Id=CountryId) From Weather Where UPPER(CityName)=?",[cityname.upper()])
                res=[]
                for i in cur:
                    for j in i:
                        res.append(j)
                # print(res)

                if fl:
                    res[0]='City: '+res[0]
                    res[1]="The temperature in next 6 hours: "+'°F '.join(res[1].split("°F"))
                    res[2]="The weather is: "+res[2]
                    res[3]="It's feeling like: "+res[3]
                    res[4]='The high and low forecast temperature today is: '+res[4]
                    res[5]='The wind now is: '+res[5]
                    res[6]='The humidity is: '+res[6]
                    res[7]='It is in: '+res[-1]

                    @app.route('/')
                    def info():
                        return render_template('name.html',my_list=res)
                    # run()
                    app.run(use_reloader=False,debug=True)
                else:
                    c1=City(res)
                    print(c1)
        else:
            print('Sorry, unrecognized command.')

# init()
if __name__ == '__main__':
    commands()

# add_city('guangzhou')

conn.commit()

# commands()
# To find the cities with modified CityNames
#
# names=[]
# cur.execute("SELECT EnglishName FROM COUNTRIES")
# for i in cur:
#     # print(i)
#     names.append(i[0])
#
# print("names:",names)
# # print(res)
# for i in res:
#     if i not in names:
#         print(i)
# Russia
# USA
# Czechia
# Venezuela
# Congo Dem. Rep.
# Vietnam
# South Korea
# Bolivia
# United Kingdom
# Iran
# Tanzania