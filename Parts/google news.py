from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta

date = str(input("Seleccione la fecha de inicio (dd/mm/yyyy): "))
keyword = input("Seleccione plataforma: " )

input_date = datetime.strptime(date, "%d/%m/%Y")
start_date = input_date.strftime("%m/%d/%Y")
end_date = (input_date + timedelta(days=7)).strftime("%m/%d/%Y")
#print(start_date)
#print(end_date)

#googlenews = GoogleNews(lang='es')
#googlenews = GoogleNews(start= start_date, end= end_date)
#googlenews.get_news(keyword + 'estrenos')

root = "https://www.google.com/"
#link = "https://www.google.com/search?q=netflix&tbs=cdr:1,cd_min:5/17/2021,cd_max:5/23/2021,lr:lang_1es&tbm=nws&sxsrf=ALeKk02FQ0nDHFXuZkZKl9uqzDedB06zpA:1621966231447&source=lnt&lr=lang_es&sa=X&ved=2ahUKEwjE9r-It-XwAhUUHLkGHRPwA5wQpwV6BAgHECA&biw=1920&bih=937&dpr=1"

main = "https://www.google.com/search?q="
dev1 = "&tbs=cdr:1,cd_min:"
dev2= ",cd_max:"
dev3= ",lr:lang_1es&tbm=nws&sxsrf=ALeKk02FQ0nDHFXuZkZKl9uqzDedB06zpA:1621966231447&source=lnt&lr=lang_es&sa=X&ved=2ahUKEwjE9r-It-XwAhUUHLkGHRPwA5wQpwV6BAgHECA&biw=1920&bih=937&dpr=1"
link = main + keyword + '+que+ver' + dev1 + start_date + dev2 + end_date + dev3
#print(link)

def news(link):
    req = Request(link, headers = {'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    with requests.Session() as c:
        soup = BeautifulSoup(webpage, 'html5lib')
        #print(soup)
        for item in soup.find_all('div', attrs={'class':'ZINbbc xpd O9g5cc uUPGi'}):
            raw_link = (item.find('a', href=True)['href'])
            link = (raw_link.split("/url?q=")[1]).split('&sa=U&')[0]

            title = (item.find('div', attrs = {'class': 'BNeawe vvjwJb AP7Wnd'}).get_text())
            description = (item.find('div', attrs = {'class': 'BNeawe s3v9rd AP7Wnd'}).get_text())

            title = title.replace (",","")
            description = description.replace (",","")

            time = description.split(" · ")[0]
            descript = description.split(" · ")[1]
            print(title)
            print(time)
            print(descript)
            print(link)
            document = open("../data.csv", "a")
            document.write("{}, {}, {}, {} \n".format(title, time, descript, link))
            document.close()
        next = soup.find('a', attrs={'aria-label':'Página siguiente'})
        next = (next['href'])
        link = root + next
        news(link)
news(link)




