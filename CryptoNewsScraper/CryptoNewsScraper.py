import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import time

#divs = soup.find_all('a')

file = open("fileone.csv","w")

csv_writer = csv.writer(file)

# gets the URL of news archives date wise
def getUrl():
    date = datetime(2001,1,1)
    while(date < datetime(2001,12,15)):
        time.sleep(1.2)
        yield "https://www.[yourWebsite].com/archive/" + date.strftime("%Y/%m/%d") + ".html" 
        date += timedelta(days = 1)
# class="text-block__link"
def returnSoup(url):
    r = requests.get(url)
    htmlContent = r.content

    soup = BeautifulSoup(htmlContent, 'html.parser')
    return soup

# the below function scraps the data to be targetted, here I've used anchor tag of website
for url in getUrl():
    soup = returnSoup(url)
    divs = soup.find_all('a')
    for aTag in divs:
        # print(url)
        if aTag.get("class") == ["text-block__link"]:
            print([aTag.text])
            csv_writer.writerow([aTag.text])

file.close()
