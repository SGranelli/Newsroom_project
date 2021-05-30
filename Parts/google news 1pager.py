from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

date = str(input("Seleccione la fecha de inicio (dd/mm/yyyy): "))
busqueda = {}
while len(busqueda) < 5:
    ingreso = input("Seleccione plataforma (hasta 5 marcas): ")
    if len(busqueda) < 5:
        busqueda['competidor' + str(len(busqueda)+1)] = str(ingreso)

for key, value in dict(busqueda).items():
    if value == "":
        del busqueda[key]

keys_values = busqueda.items()
busqueda = {str(key): value.replace(" ", "+") for key, value in keys_values}
#print(busqueda)

## ver cómo llevar a una interfaz gráfica

#keyword = input("Seleccione plataforma: " )

input_date = datetime.strptime(date, "%d/%m/%Y")
start_date = input_date.strftime("%m/%d/%Y")
end_date = (input_date + timedelta(days=7)).strftime("%m/%d/%Y")
#print(start_date)
#print(end_date)


count = 0
while (count < len(busqueda)):
    count = count + 1
    root = "https://www.google.com/"
    main = "https://www.google.com/search?q="
    dev1 = "&tbs=cdr:1,cd_min:"
    dev2 = ",cd_max:"
    dev3 = ",lr:lang_1es&tbm=nws&sxsrf=ALeKk02FQ0nDHFXuZkZKl9uqzDedB06zpA:1621966231447&source=lnt&lr=lang_es&sa=X&ved=2ahUKEwjE9r-It-XwAhUUHLkGHRPwA5wQpwV6BAgHECA&biw=1920&bih=937&dpr=1"

    brand = busqueda['competidor' + str(count)]

    link = main + brand + '+estrenos+semana+argentina' + dev1 + str(start_date) + dev2 + str(end_date) + dev3
    #print(link)

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

            document = open("../data.csv", "a", encoding='utf-8')
            document.write("{}, {}, {}, {}, {} \n".format(title, time, descript, link, brand))
            document.close()



## Sentiment
headerlist = ['title', 'time', 'descript', 'link', 'brand']
df = pd.read_csv("../data.csv", dtype =str, names = headerlist)

analyzer = SentimentIntensityAnalyzer()

negative = []
neutral = []
positive = []

for n in range(df.shape[0]):
    title = df.iloc[n, 0]
    description = df.iloc[n, 2]
    title_analyzed = analyzer.polarity_scores(title)
    description_analyzed = analyzer.polarity_scores(description)
    negative.append(((title_analyzed['neg']) + (description_analyzed['neg'])) / 2)
    neutral.append(((title_analyzed['neu']) + (description_analyzed['neu'])) / 2)
    positive.append(((title_analyzed['pos']) + (description_analyzed['pos'])) / 2)

df["Negative"] = negative
df["Neutral"] = neutral
df["Positive"] = positive

df.to_csv('data.csv',index=False)


#pd.set_option('display.max_columns', None)
#print(df.head())


## Word cloud

#col_list = ['title', 'time', 'descript', 'link','brand']
#df = pd.read_csv('data2.csv', usecols=col_list)
#print(df.head())
#df = open('data2.csv', 'r', encoding='utf-8').read()

#Contenido
text = df[['title', 'descript']]
#print(text)
#text = open('data2.csv', 'r', encoding='utf-8').read()
stopwords = set(STOPWORDS)

#Appearance
wc = WordCloud(background_color= 'white', max_font_size=50, max_words= 100, stopwords= stopwords, repeat=False)
wc.generate(str(text))

#plotting
plt.imshow(wc, interpolation = 'bilinear')
plt.axis('off')
plt.show()

