import dash                              # pip install dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Output, Input
from datetime import datetime
from datetime import timedelta
from dash_extensions import Lottie       # pip install dash-extensions
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
import plotly.express as px              # pip install plotly
import pandas as pd                      # pip install pandas
from datetime import date
import calendar
from wordcloud import WordCloud, STOPWORDS
import plotly.figure_factory as ff
import matplotlib.pyplot as plt



fecha = "17/5/2021"
input_date = datetime.strptime(fecha, "%d/%m/%Y")
start_date = input_date.strftime("%m/%d/%Y")
end_date = (input_date + timedelta(days=7)).strftime("%m/%d/%Y")

#headerlist = ['title', 'time', 'descript', 'link', 'brand','negative','neutral','positive']
df = pd.read_csv("data.csv")
busqueda = {'competidor1': 'lionel messi', 'competidor2': 'amazon+prime+video', 'competidor3': 'disney+plus'}

#df.to_csv('data.csv',index=True)
df['brand_filtered']=df['brand']
df['brand_filtered']=df['brand_filtered'].str.replace('+',' ',regex=False)

#pd.set_option('display.max_columns', None)
#print(df.head())

keys_values = busqueda.items()
busqueda = {str(key): value.replace("+", " ") for key, value in keys_values}
#print(busqueda.values())


values = busqueda.values()
values_list = list(values)
#print(values_list)

#labels = [{'label': values_list[0], 'value' : values_list[0]} , {'label' : values_list[1], 'value' : values_list[1]}, {'label' : values_list[2], 'value' : values_list[2]}]
#print(labels)

lista_copy = []
i = 0
while i < len(values_list):
    i = i+1
    lista_copy.append({'label' : values_list[i-1], 'value' :values_list[i-1]})

#lista_copy = [{'label': 'netflix', 'value': 'netflix'}, {'label': 'amazon prime video', 'value': 'amazon prime video'}, {'label': 'disney plus', 'value': 'disney plus'}]
#print(labels)

# Bootstrap themes by Ann: https://hellodash.pythonanywhere.com/theme_explorer
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
                        labelStyle={"margin-right": "100px" , 'display': 'inline', 'padding-left': '20px'}),
                ])
            ]),
        ], width=7),
        dbc.Col([
            dbc.Card([
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
    app.run_server(debug=True)
