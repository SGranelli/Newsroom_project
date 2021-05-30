from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import csv
import pandas as pd

col_list = ['title', 'time', 'descript', 'link','brand']
df = pd.read_csv('data.csv', usecols=col_list)
#print(df.head())

#df = open('data2.csv', 'r', encoding='utf-8').read()


#Contenido
text = df[['title', 'descript']]
#print(text)
#text = open('data2.csv', 'r', encoding='utf-8').read()
stopwords = set(STOPWORDS)

#Appearance
wc = WordCloud(background_color= 'white', max_font_size=50, max_words= 50, stopwords= stopwords, repeat=False)
wc.generate(str(text))

#plotting
plt.imshow(wc, interpolation = 'bilinear')
plt.axis('off')
#plt.show()


#document = open("wordcount.csv", "a", encoding='utf-8')
#document.write("{} \n".format(wc))
#document.close()


text.to_csv('data3.csv',index=False)