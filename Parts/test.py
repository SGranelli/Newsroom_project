from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import pandas as pd


df = pd.read_csv('data.csv', dtype =str)

df['brand_filtered']=df['brand']
#print(df['brand_filtered'])

df['brand_filtered']=df['brand_filtered'].str.replace('+',' ',regex=False)
#print(df['brand_filtered'])
#print(df)

dff = df[df['brand_filtered'].str.contains('lionel messi')].astype(str)
print(dff)