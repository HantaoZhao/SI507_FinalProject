# SI507_FinalProject

## Data Source:	
> - For the first part, including weather forecasts and weather conditions, the data are from https://www.timeanddate.com/. All the information are scraped from the website.
> - For the second part, including the name and region of different countries, the data are from countries.json

## Other Information
> No secret file is necessary for this program.
> It takes sometime to scrape data from the website. 
> Therefore, use the cache and the established database for testing purposes.
> Some part of the program uses flask, and the webpage can be opened in a browser.
> The requirements.txt can be found in the folder. 
> Some unrelated python packages are hidden(such as tensorflow). 
> If the program can't run properly, please contact me.

## Brief Description
> A "City" class is constructed. 
> Each city has following attibutes: CityName, Temperature for next 6 hours, Weather, Feel Temperature, High and Low Forecast Temperature, Wind Condition, Humidity, CountryId(It is a foreign key)
> A __str__() function is defined to conveniently and clearly output the information for each city.
> 
> A database is established. It includes two tables: 
> - 1. Country. It contains information about each country, such as country name, and the region it is in.
> - 2. Weather. It contains information about each city, including the attributes of the City class mention above.
>
> Some of the most important data processing functions:
> - 1. city_search(city_name,Country,City)
> This function scrapes information from the webpage for each city.
> - 2. city_init()
> This function scrapes the weather conditions of all the popular cities on the website.
> - 3. add_city(cityname)
> This function adds a city to the database if it does not exist. For the sake of simpilicity, only the most relevant city is added.

## Brief User Guide:
#### You can run the program and use 'help' command to see a more formatted output.
> Commands available:
> 
> exit
>     Terminate the program.
> 
> help
>     Print the instructions for the program. 
>     
> all
>     Print the weather conditions of every city in the database.
> 
> city <CityName>
>     Show the weather conditions of a city. 
>     The parameter <CityName> is required. For example: Ann Arbor, New York, Chicago, Washington DC
> 
> flask city <CityName>
>     Show the weather conditions of a city. 
>     The parameter <CityName> is required. For example: Ann Arbor, New York, Chicago, Washington DC
>     Must rerun the program if flask is used.
> 
> country <CountryName>
>     Show the weather conditions of cities in a country.
>     The parameter <CountryName> is required. For example: USA, Canada, United Kingdom, Germany
> 
> region <RegionName>
>     Show the weather conditions of cities in a region.
>     The parameter <RegionName> is required. For example: Asia, Europe, Americas, Africa
