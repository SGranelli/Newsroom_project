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


## P1 SCRAPPING DE NOTICIAS

fecha = str(input("Seleccione la fecha de inicio (dd/mm/yyyy): "))
busqueda = {}
while len(busqueda) < 5:
    ingreso = input("Ingrese termino de busqueda (max 5): ")
    if len(busqueda) < 5:
        busqueda['competidor' + str(len(busqueda)+1)] = str(ingreso)

for key, value in dict(busqueda).items():
    if value == "":
        del busqueda[key]

keys_values = busqueda.items()
busqueda = {str(key): value.replace(" ", "+") for key, value in keys_values}
#print(busqueda)

#keyword = input("Seleccione plataforma: " )

input_date = datetime.strptime(fecha, "%d/%m/%Y")
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

    link = main + brand + dev1 + str(start_date) + dev2 + str(end_date) + dev3
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
            #print(title)
            #print(time)
            #print(descript)
            #print(link)

            document = open("data.csv", "a", encoding='utf-8')
            document.write("{}, {}, {}, {}, {} \n".format(title, time, descript, link, brand))
            document.close()



## P2 ANÁLISIS DE SENTIMENT

headerlist = ['title', 'time', 'descript', 'link', 'brand']
df = pd.read_csv('data.csv', dtype =str, names = headerlist)

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

df.to_csv('data.csv',index=True)
#print(df["Negative"].mean())

## P3 VISUALIZADOR


keys_values = busqueda.items()
new_busqueda = {str(key): value.replace("+", " ") for key, value in keys_values}

values = new_busqueda.values()
values_list = list(values)


df.to_csv('data.csv',index=True)
df['brand_filtered']=df['brand']
df['brand_filtered']=df['brand_filtered'].str.replace('+',' ',regex=False)


lista_copy = []
i = 0
while i < len(values_list):
    i = i+1
    lista_copy.append({'label' : values_list[i-1], 'value' :values_list[i-1]})


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

LogoGN = '/assets/logoGN.png'

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src=LogoGN) # 150px by 45px
            ], color='warning', outline=True),
        ], width=1),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H1('Newsroom Dashboard',className='mt-1 mb-1'),
                ], style={'textAlign':'center','textColor':'text-white'})
            ], color='warning', inverse=True),
        ], width=9),
    ], className='mb-2'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Datos relevados desde:"),
                dbc.CardBody([
                    html.P(str(start_date) + " al " + str(end_date), className="card-text"),
                ])
            ]),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Términos buscados"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id='radio_filter',
                        options=lista_copy,
                        value=str(values_list[0]),
                        #inputStyle={'display': 'inline'},
                        labelStyle={"margin-right": "100px" , 'display': 'inline'}),
                ])
            ]),
        ], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Ver archivo"),
                html.Div(
                    [
                        html.Button("Abrir CSV", id="btn_csv",className="mt-auto"),
                        dcc.Download(id="download-dataframe-csv"),
                    ]
                )
            ]),
        ], width=1),
    ], className='mb-2'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='table_data', children=[]),
                ])
            ]),
        ], width=10),
    ], className='mb-2'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='wordcloud', figure={}, config={'displayModeBar': False}),
                ])
            ]),
        ], width=5),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='pie-chart', figure={}, config={'displayModeBar': False}),
                ])
            ]),
        ], width=5),
    ],className='mb-2'),
], fluid=True)

# Nube de palabras ************************************************************

@app.callback(
    Output('wordcloud','figure'),
    Input('radio_filter','value')
)
def update_wc(filter):

    dff = df[df['brand_filtered'].str.contains(str(filter))]
    dff['text_to_use'] = dff['title'] + dff['descript']

    #print(dff)
    text = dff['text_to_use']
    stopwords = set(STOPWORDS)

    # Appearance
    wc = WordCloud(background_color='white', max_font_size=50, max_words=50, stopwords=stopwords, repeat=False)
    wc.generate(str(text))

    fig_wordcloud = px.imshow(wc, template='ggplot2',
                              title="Principales Términos")
    fig_wordcloud.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    return fig_wordcloud

# Pie Chart ************************************************************
@app.callback(
    Output('pie-chart','figure'),
    Input('radio_filter','value')
)
def update_pie(filter):

    dff = df[df['brand_filtered'].str.contains(str(filter))]

    positive = dff["Positive"].mean()
    negative = dff["Negative"].mean()
    neutral = dff["Neutral"].mean()

    fig_pie = px.pie(names=['Positive','Negative', 'Neutral'], values=[positive, negative, neutral],
                     template='ggplot2', title="Sentiment"
                     )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_pie.update_traces(marker_colors=['green','red', 'yellow'])

    return fig_pie

# Table Data ************************************************************
@app.callback(
    Output('table_data','children'),
    Input('radio_filter','value')
)

def table(filter):

    dff = df[df['brand_filtered'].str.contains(str(filter))]
    tooltip_data = df['descript']




    return [
        dash_table.DataTable(
            id='filtered_table',
            columns=[{"name": 'Principales Noticias', "id": i} for i in (dff[['title']]).columns],
            data=dff.to_dict('records'),
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
            },
            page_size = 10,
            style_header = {
                'backgroundColor': 'grey',
                'fontBody': 'light',
                'fontWeight': 'bold',
            },
            tooltip_data=[
                {
                    column: {'value': row['descript'] + '\n\n' + row ['link'] , 'type': 'markdown'}
                    for column, value in row.items()
                } for row in dff.to_dict('records')
            ],
            tooltip_duration=None)
    ]

### Open
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "data.csv")

## Ejecución
if __name__=='__main__':
    app.run_server(debug=True, port=8004, use_reloader=False)