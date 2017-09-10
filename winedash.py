import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import flask

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

df = pd.read_excel('Wines.xlsx')
countries = df['Country'].unique()
vendor_location_countries = df['Vendor_location'].unique()
vendor_names = df["Vendor_name"].unique()
regions = df["Region"].unique()

links_list = [[],[],[],[]]

styles = {
    'column': {
        'display': 'inline-block',
        'width': '33%',
        'padding': 10,
        'boxSizing': 'border-box',
        'minHeight': '200px'
    },
    'pre': {'border': 'thin lightgrey solid'}
}

# Append an externally hosted CSS stylesheet
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
#    "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
})

markdown_div = dcc.Markdown(''' 
### Data Sommelier - make your wine purchases better informed

Use the wigdets to find the best option
''')

hover_data = html.Div([
        dcc.Markdown("**Wine basket** - Click on the dots to save the links.".replace('   ', '')),
        html.Pre(id='hover-data', style=styles['pre'])
    ])

click_data = html.Div([
        dcc.Markdown("**Click Data** - Click over values in the graph.".replace('   ', '')),
        html.Pre(id='click-data', style=styles['pre'])
    ])


def generate_table(df, max_rows=5):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df[["Name","Winery","Region","Price","Rating","Name_link"]].columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df[["Name","Winery","Region","Price","Rating","Name_link"]].columns
        ]) for i in range(min(len(df), max_rows))],
        className = "u-full-width"
    )


def generate_links_table(links_list):
    links = links_list[0]
    names = links_list[1]
    prices = links_list[2]
    ratings = links_list[3]
    links_section = [html.Pre(
                html.A("- " + names[i] + " - " + str(ratings[i]) + " - R$: " + str(prices[i]),
                    href= links[i],
                    target="_blank"
                )
                ,style=styles['pre']
            )
        for i in range(0,len(links),2)
        ]


    return html.Div(links_section ,id="links-list")


def generate_better_table(df, max_rows=5):

    return dt.DataTable(
                #rows=df[["Name_link","Winery","Region","Price","Rating"]][:max_rows].to_dict('records'),
                rows=df[["Name_link", "Winery", "Region", "Price", "Rating"]][:max_rows].to_dict('records'),
                filterable=False,
                sortable=True,
                id='datatable'
    )


country_dd = html.Div([
                dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in countries],
                value=[],
                multi=True
                )
            ], style={'width': '70%'}, className ="u-full-width")
vendor_location_dd = html.Div([
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': i, 'value': i} for i in vendor_location_countries],
                            value=[],
                            multi=True
                        )
                    ],style={'width': '70%'})
vendor_dd = html.Div([
                dcc.Dropdown(
                id='vendor-name',
                options=[{'label': i, 'value': i} for i in vendor_names],
                value=[],
                multi=True
                )
            ], style={'width': '70%'}, className ="u-full-width")
region_dd = html.Div([
                dcc.Dropdown(
                id='regions',
                options=[{'label': i, 'value': i} for i in regions],
                value=[],
                multi=True
                )
            ], style={'width': '70%'}, className ="u-full-width")
price_slider = dcc.Slider(id='year--slider',min=df['Price'].min(),max=df['Price'].max(),value=df['Price'].max(),step=10)
app.layout = html.Div([
        html.Div(
            [markdown_div
             ],
            className="row"
        ),
        html.Div(
            [
            html.Div(
                [
                 html.Div("Wine country"),
                 country_dd,
                 html.Div("Region"),
                 region_dd,
                 html.Div("Vendor based in"),
                 vendor_location_dd,
                 html.Div("Vendor name"),
                 vendor_dd,
                 html.Div("Maximum price"),
                 price_slider
                 ],
                className="three columns"
            ),
            html.Div(
                [html.Div([
                    dcc.Graph(id='indicator-graphic')
                 ],
                style={"border-style": "ridge"}
            )],className="five columns"
            ),
            html.Div(
                [hover_data,
                 generate_links_table(links_list)
                 ],
                className="three columns"
            )],
            className="row"
        )
    ])

@app.callback(dash.dependencies.Output('indicator-graphic', 'figure'), [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('year--slider','value'),
     dash.dependencies.Input('vendor-name','value'),
     dash.dependencies.Input('regions', 'value')
     ])
def update_graph(xaxis_column_name, yaxis_column_name,year_value, vendor,region_value):

    #dff = df[(df["Price"] < year_value) &
    #         (df["Country"].isin(list(xaxis_column_name))) &
    #         (df["Vendor_location"].isin(list(yaxis_column_name))) &
    #         (df["Region"].isin(list(region_value))) &
    #         (df["Vendor_name"].isin(list(vendor)))
    #]

    dff = df
    if xaxis_column_name: dff = dff[dff["Country"].isin(list(xaxis_column_name))]
    if yaxis_column_name: dff = dff[dff["Vendor_location"].isin(list(yaxis_column_name))]
    if year_value: dff = dff[dff["Price"] < year_value]
    if vendor: dff = dff[dff["Vendor_name"].isin(list(vendor))]
    if region_value: dff = dff[dff["Region"].isin(list(region_value))]

    return {
        'data': [go.Scatter(
            x=dff['Price'],
            y=dff['Rating'],
            text= dff['Name'],
            hoverinfo=dff['Link'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': "Price (R$)",
                'type': 'linear'
            },
            yaxis={
                'title': "Rating (0-5)",
                'type': 'linear'
            },
            margin={'l': 30, 'b': 30, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


@app.callback(dash.dependencies.Output('hover-data', 'children'),[dash.dependencies.Input('indicator-graphic', 'hoverData')])
def display_hover_data(hoverData):
    return hoverData['points'][0]['hoverinfo']


@app.callback(dash.dependencies.Output('links-list', 'children'),[dash.dependencies.Input('indicator-graphic', 'clickData')])
def display_click_data(clickData):
    links_list[0].append(clickData['points'][0]['hoverinfo'])
    links_list[1].append(clickData['points'][0]['text'])
    links_list[2].append(clickData['points'][0]['x'])
    links_list[3].append(clickData['points'][0]['y'])
    return generate_links_table(links_list)


if __name__ == '__main__':
    app.run_server(debug=True)