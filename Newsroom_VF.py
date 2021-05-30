## NEWSROOM REPORT
## El objetivo de este proyecto es poder conocer cuáles son las principales noticias vinculadas a tópicos buscados por el usuario.
## La fuente del relevamiento será Google News y los datos corresponderán a 7 días desde la fecha de inicio (ingresada por el usuario).
## Del usuario entonces se pedirá una fecha de inicio y los términos a buscar (hasta 5 en total)
## Finalmente, se generará un dashboard que permitirá ver la información relevada de una manera dinámica.
## También se genera un archivo CSV el cual se puede obtener desde el dashboard.


## A continuación, se detallas las librerías utilizadas para generar este proyecto.
## Además de las vistas en el curso, como BeautifulSoup, se incluyeron algunas como Dash para la generación de la app
## También se utiliza wordcloud para la generación de una nube de palabras con los términos más repetidos de las noticias relevadas
## Por su parte, vaderSentiment permitirá hacer una clasificación de los términos en positivos, negativos y neutrales para mostrar el 'sentiment' de la búsqueda

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

## En esta sección, se realizará la búsqueda de noticias de los términos ingresados.
## A través de inputs, el usuario deberá ingresar la fecha de inicio de búsqueda y los términos a indagar (hasta 5 en total). Si el usuario quiere hacer menos de 5 búsquedas,
## solamente deja la búsqueda vacía avanzando con Enter. Cada búsqueda ingresada se irá almacenando en un diccionario que será utilizado para ir dinamizando el link de búsqueda.
## Se agrega un proceso de 'normalización' de términos, agregando un + en cada espacio entre términos, para que la búsqueda no arroje un mensaje de error.


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

## Se 'normalizan' las fechas, desde el inicio, y se calcula la fecha de búsqueda final (7 días desde el input del usuario).
## Estas variables también serán utilizadas para definir el link de búsqueda final.

input_date = datetime.strptime(fecha, "%d/%m/%Y")
start_date = input_date.strftime("%m/%d/%Y")
end_date = (input_date + timedelta(days=7)).strftime("%m/%d/%Y")
#print(start_date)
#print(end_date)


## Se da comienzo a un loop que finalizará solo cuando la cantidad de iteraciones sea igual a la longitud del diccionario generado a través del input del usuario.
## El link de búsqueda está compuesto por partes estáticas (almacenadas en variables) y las partes dinámicas que corresponden al input generado anteriormente.
## Cada vez que se genera la iteración, esta variable se irá actualizando, recorriendo cada uno de los valores que componen el diccionario

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


## Se inicia el proceso de búsqueda de la información, donde se extraerán piezas como título de la noticia, copete, tiempo de publicación y link.
## Para hacer esta búsqueda, se van definiendo items específicos que se encontrarán en el código HTML del sitio.
## La idea es ir haciendo los reemplazos de símbolos, espacios y demás strings para dejar cada variable apta para mostrar.

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

## Luego de relevada la información, se genera un archivo CSV donde se incluyen las variables relevadas y mencionadas anteriormente.
## Este archivo CSV se irá actualizando con la información relevada por cada iteración, de manera de garantizar que no haya pérdida de infomación en cada vuelta.

            document = open("data.csv", "a", encoding='utf-8')
            document.write("{}, {}, {}, {}, {} \n".format(title, time, descript, link, brand))
            document.close()



## P2 ANÁLISIS DE SENTIMENT

## En esta sección, trabajaremos con el archivo 'csv' generado en la búsqueda inicial y se procederá a hacer un análisis de 'sentiment' de los términos mencionados en título y copete.
## Para esto se utiliza la librería vaderSentiment, la cual nos permitirá clasificar las noticias en positivas, neutrales y negativas.
## Una vez hecha la clasificación, se actualizará el DF con la información relevada, agregando una columna para cada sentiment
## El valor que corresponde al sentiment es un porcentaje promedio entre el % de sentiment del título y el % del sentiment del copete.
## La actualización del DF se verá también reflejada en el CSV con el que venimos trabajando


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

## P3 VISUALIZADOR

## En esta sección se desarrolla el dashboard de visualización, donde podremos ver los principales titulares de cada término de búsqueda, el sentiment y una nube de palabras.
## En esta primera parte se volverá a normalizar el string que corresponde a cada término de búsqueda, eliminando el signo + y volviéndolo a reemplazar por espacio.
## Esto es una transformación estética para que se muestren correctamente los filtros que figuran en el dashboard.
## Se genera también una variable que almacena una lista con una serie de parámetros que serán utilizados para la configuración del botón de radio que permitirá filtrar la información mostrada.
## Esto se hace porque, como la búsqueda es dinámica y se actualiza cada vez que el usuario utiliza la app, no se puede dejar con valores pre establecidos.

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


## A continuación, se genera el layout de la app. El mismo consiste en 4 filas, con variable cantidad de columnas.
## La primera fila muestra dos columnas, una con el logo de GNews y otra con el título de la herramienta.
## La segunda fila cuenta con 3 columnas: la primera muestra el período en el que se relevó la información, de acuerdo al input del usuario,
## la siguiente columna muestra los términos de búsqueda ingresados en formato de botón de radio, para seleccionar qué información mostrar en la visualización,
## y la útlima columna muestra el botón de descarga para abrir el archivo 'csv' con la información relevada.
## Las estructuras se completan con componentes Dash (librería utilizada para generar la app), donde se indica qué tipo de componente es, y se asigna la configuración del mismo
## en términos de funcionalidad, a qué datos refiere, y cuestiones más estéticas.
## De este grupo, el botón de radio funcionará como un filtro que determina qué información mostrar y que va actualizando el DF en función de la selección.
## Esta actualización se genera en un 'back end', o app callbacks, que tomarán el input del filtro, harán las modificaciones pertinentes y devolverán el gráfico o información a mostrar.

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

## NUBE DE PALABRAS ************************************************************

## Este callback responde a la cuarta fila del layout, primera columna
## La función de callback toma el input del filtro generado por el botón de radio y devuelve una función definida.
## La función lo que hace es crear una nueva variable a partir del DF original (para mantenerlo sin modificaciones y no alterar la dinámica de la app), con los datos que respondan al
## filtro seleccionado anteriormente. Una vez generada esta variable, se genera una nueva solo con la información de título y descripción para generar la nube de palabras.
## Se utiliza la librería WordCloud para la generación de esta nube con los términos de búsqueda más mencionados, llamando a la variable creada previamente.
## Luego se determinan cuestiones estéticas de visualización de la nube y finalmente se devuelve esta 'figura' que es la que la app asigna como output.


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

## PIE CHART ************************************************************

## Este callback responde a la cuarta fila del layout, segunda columna
## Se trata de un pie chart que permitirá ver la clasificación de sentiment obtenida anteriormente.
## La dinámica es similar a la descripta anteriormente para la nube de palabras: un input que depende del filtro seleccionado,
## la generación de una copia del DF con los valores filtrados y la generación de variables positivas, negativas y neutras que serán las que serán tenidas en cuenta
## por el gráfico para generar la visualización final.
## Se asignan nuevamente los parámetros que hacen a la estética del gráfico y se genera el output que tomará el callback para mostrar.

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

## TABLA TITULARES ************************************************************

## Este callback responde a la tercera fila del layout
## Se trata de una tabla con los principales titulares relevados.
## En este caso, se genera la tabla con parámetros que hacen a la estética de la misma, pero también se incluye la posibilidad de ver
## el copete y el link de la noticia cuando nos desplazamos a través de cada titular.
## La dinámica de filtro, actualización y output final es la misma que se mencionó en los otros componentes.

@app.callback(
    Output('table_data','children'),
    Input('radio_filter','value')
)

def table(filter):

    dff = df[df['brand_filtered'].str.contains(str(filter))]

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

## DOWNLOAD  ************************************************************

## Este callback responde a la acción del botón de descarga.
## El input, en este caso, corresponde a la acción del botón (click) y la respuesta u output es la actualización del archivo CSV con el que venimos trabajando y la posterior descarga


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "data.csv")


## EJECUCIÓN  ************************************************************

if __name__=='__main__':
    app.run_server(debug=True, port=8004, use_reloader=False)