import pandas as pd 
import dash  
import dash_core_components as dcc  
import dash_html_components as html 
import plotly.graph_objects as go 
import dash_table
from sqlalchemy import create_engine

Username='postgres'
Password='rlNTf1fnKCJF7vXR1tbo'
Host='nps-demo-instance.cxvffngu96fr.us-east-2.rds.amazonaws.com'
db_name='strategy'
connect_database='postgresql://{}:{}@{}/{}'.format(Username,Password,Host,db_name)

engine = create_engine(connect_database)
df=pd.read_sql("SELECT * FROM trades", engine.connect(),parse_dates=('entry_time'))
#Import the CSV file into a DataFrame 
#df = pd.read_csv('C:\\Users\\Santiago\\OneDrive - Universidad de los andes\\Cursos\\MinTic\\Homeworks\\extended_case_4_student\\extended_case_4_student\\aggr.csv',parse_dates=['entry_time']) 
df['YearMonth']=df['entry_time'].apply(lambda x: "{}-{}".format(x.year, x.month))

#Functions
## Filtered function
def filter_df(data,Exchange,Margin,start_date,end_date):
    df_f=data[(data['exchange']==Exchange) & (data['margin']==Margin) & 
              (data['entry_time'] >= start_date) & (data['entry_time'] <= end_date)]
    return df_f

def month_return(df_f):
    out=[]

    for name, group in df_f.groupby('YearMonth'): 
        exit_balance = group.head(1)['exit_balance'].values[0]
        entry_balance = group.tail(1)['entry_balance'].values[0]
        monthly_return = (exit_balance*100 / entry_balance)-100
        out.append({
            'month': name,
            'entry': entry_balance,
            'exit' : exit_balance,
            'monthly_return': monthly_return
        })
    return out

def calc_btc_returns(dff):
    btc_start_value = dff.tail(1)['btc'].values[0]
    btc_end_value = dff.head(1)['btc'].values[0]
    btc_returns = (btc_end_value * 100/ btc_start_value)-100
    return btc_returns

def calc_strat_returns(dff):
    start_value = dff.tail(1)['exit_balance'].values[0]
    end_value = dff.head(1)['entry_balance'].values[0]
    returns = (end_value * 100/ start_value)-100
    return returns

#Make Dash App 
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])

app.layout = html.Div(children=[
    html.Div(children=[
        html.H2(children="Bitcoin Leveraged trading bascket analysis",className='h2-title')
    ], className='study-browser-banner row'),

    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Exchange"),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label,'value': label} for label in df['exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Leverage"),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['margin'].unique()
                                        ],
                                        value=3,
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="three columns card",
                                children=[
                                    html.H6("Select a Date Range"),
                                    dcc.DatePickerRange(
                                        id='date-range-select',
                                        display_format="MMM YY",
                                        start_date=df['entry_time'].min(),
                                        end_date=df['entry_time'].max(),
                                        min_date_allowed=df['entry_time'].min(),
                                        max_date_allowed=df['entry_time'].max(),
                                        initial_visible_month=df['entry_time'].max()
                                    )
                                ]
                            ),
                            html.Div(
                                id="strat-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-returns", className="indicator_value"),
                                    html.P('Strategy Returns', className="twelve columns indicator_text")
                                ]
                            ),
                            html.Div(
                                id="market-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-returns", className="indicator_value"),
                                    html.P('Market Returns', className="twelve columns indicator_text")
                                ]
                            ),
                            html.Div(
                                id="strat-vs-market-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-vs-returns", className="indicator_value"),
                                    html.P('Returns vs Market', className="twelve columns indicator_text")
                                ]
                            )                                                        
                        ]
                    )
                ]
            ),
            html.Div(
                className="twelve columns card",
                children=[
                    dcc.Graph(
                        id="monthly-chart",
                        figure={
                            'data':[]
                        }
                    )
                ]
            ),
            html.Div(
                className="padding row",
                children=[
                    html.Div(
                        className="six columns card",
                        children=[
                            dash_table.DataTable(
                                id='table',
                                columns=[
                                    {'name': 'Number', 'id': 'Number'},
                                    {'name': 'trade_type', 'id': 'trade_type'},
                                    {'name': 'Exposure', 'id': 'Exposure'},
                                    {'name': 'entry_balance', 'id': 'entry_balance'},
                                    {'name': 'exit_balance', 'id': 'exit_balance'},
                                    {'name': 'pnl', 'id': 'pnl'}
                                ],
                                style_cell={'width': '50px'},
                                style_table={
                                    'maxHeight': '450px',
                                    'overflowY': 'scroll'
                                }
                            )
                        ]
                    ),
                    dcc.Graph(
                        id="pnl-types",
                        className="six columns card",
                        figure={
                            'data':[]
                        }
                    )
                ]
            ),
            html.Div(
                className="padding row",
                children=[
                    dcc.Graph(
                        id="daily-btc",
                        className="six columns card",
                        figure={}
                    ),
                    dcc.Graph(
                        id="balance",
                        className="six columns card",
                        figure={}
                    )
                ]
                )
        ]
    )
])
@app.callback(
    [dash.dependencies.Output('date-range-select','start_date'),
     dash.dependencies.Output('date-range-select','end_date')],
     [dash.dependencies.Input('exchange-select','value')]
)
def update_date_range(x):
    min_date=df['entry_time'][df['exchange'] == x].min()
    max_date=df['entry_time'][df['exchange'] == x].max()
    return min_date, max_date

@app.callback(
    [
        dash.dependencies.Output('monthly-chart','figure'),
        dash.dependencies.Output('market-returns', 'children'),
        dash.dependencies.Output('strat-returns', 'children'),
        dash.dependencies.Output('market-vs-returns', 'children')
    ]
    ,
    [
        dash.dependencies.Input('exchange-select','value'),
        dash.dependencies.Input('leverage-select','value'),
        dash.dependencies.Input('date-range-select','start_date'),
        dash.dependencies.Input('date-range-select','end_date')
    ]
)
def update_monthly(exchange,leverage,start_date,end_date):
    dff=filter_df(df,exchange,leverage,start_date,end_date)
    mr=month_return(dff)
    btc_returns = calc_btc_returns(dff)
    strat_returns = calc_strat_returns(dff)
    strat_vs_market = strat_returns - btc_returns
    return {
        'data':[
            go.Candlestick(
                x=[each['month'] for each in mr],
                open=[each['entry']for each in mr],
                close=[each['exit']for each in mr],
                low=[each['entry'] for each in mr],
                high=[each['exit'] for each in mr]
            )
        ],
        'layout': {
            'title': 'Overview of Monthly Performance'
        }
    }, f'{btc_returns:0.2f}%', f'{strat_returns:0.2f}%', f'{strat_vs_market:0.2f}%'

@app.callback(
    [
        dash.dependencies.Output('table', 'data'),
        dash.dependencies.Output('pnl-types', 'figure')
    ],
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_table(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    data=[]
    for i in dff['trade_type'].unique():
        data.append(
            go.Bar(
                x=dff['entry_time'][dff['trade_type']==i],
                y=dff['pnl'][dff['trade_type']==i],
                name=i
            )
        )
    mylayout = go.Layout(
        title='Loss-profit',
        showlegend=True,
        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
        height= 500
    )
    
    fig= {'data': data, 'layout':mylayout}
    return dff.to_dict('records'), fig

# line plots 
@app.callback(
    [
        dash.dependencies.Output('daily-btc','figure'),
        dash.dependencies.Output('balance','figure'),
    ],
    [
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_lineplots(start,end):
    dfline=df[['entry_time','btc','exit_balance']][(df['entry_time'] >= start) & (df['entry_time'] <= end)].sort_values(by=['entry_time'])
    btcdata=[
        go.Scatter(
            x=dfline['entry_time'],
            y=dfline['btc'],
            mode='lines'
            )
    ]
    btclayout=go.Layout(
        title='btc',
        height= 500
    )
    btcplot={'data': btcdata, 'layout': btclayout}

    baldata=[
        go.Scatter(
            x=dfline['entry_time'],
            y=dfline['exit_balance'],
            mode='lines'
            )
    ]
    ballayout=go.Layout(
        title='Balance',
        height= 500
    )
    balplot={'data': baldata, 'layout': ballayout}
    return balplot, btcplot

if __name__ == "__main__":
    app.run_server(debug=True) 

