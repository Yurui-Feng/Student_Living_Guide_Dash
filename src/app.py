from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

########## reading the data ###########
df = pd.read_csv("https://raw.githubusercontent.com/Yurui-Feng/Student_Living_Guide_Dash/main/data/processed/processed_data.csv")
indices = df.columns[2:8].tolist()
countries = df["Country"].unique().tolist()
continent = df["Continent"].unique().tolist()

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("Student Living Guide"),
        html.Hr(),
        html.P(
            "A dashboard provides information about the cost of living in different countries.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Map", href="/", active="exact"),
                dbc.NavLink("Histogram", href="/page-1", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),
        html.H5("Index", style={'textAlign': 'center'}),
        dcc.Dropdown(id="select_index",options=indices,value = indices[0]),
        html.Br(),
        html.H5("Country", style={'textAlign': 'center'}),
        dcc.Dropdown(id="select_country",options=countries,value = "United States"),
        html.Br(),
        html.H5("Continent", style={'textAlign': 'center'}),
        dcc.Dropdown(id="select_continent",options=continent,value = "North America", multi=True)
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), 
              #Output("graph", "figure"), 
              Input("url", "pathname"),
              Input("select_index", "value"),
              Input("select_country", "value"),
              Input("select_continent", "value"))

def render_page_content(pathname,index, country, continent):
    lat = df[df["Country"] == country]["latitude"].values[0]
    long  = df[df["Country"] == country]["longitude"].values[0]
    val = df[df["Country"] == country][index].values[0]
    if type(continent) == list or not continent:
        scope = "world"
        filtered_df = df[df["Continent"].isin(continent)]
    else:
        scope = continent.lower()
        filtered_df = df[df["Continent"]==continent]
    map = px.choropleth(
        df, 
        locations="Country", 
        locationmode="country names", 
        color=index,
        color_continuous_scale = "Viridis",
        projection='equirectangular',
        hover_name="Country", 
        hover_data=[index],
        )
    map.update_layout(height=400, 
                      margin={"r":0, "t":0, "l":0, "b":0},
                      coloraxis_colorbar=dict(title="Magnitude"))
    #map.update_geos(scope=scope)
    map.add_trace(go.Scattergeo(
        lon=[long],
        lat=[lat],
        mode='markers',
        marker=dict(size=10, symbol='arrow-bar-up'),
        text=[country],
        showlegend=False,
        hovertemplate=country,
    ))

    hist = px.histogram(
        filtered_df, nbins=20,
        x=index)
    hist.update_traces(marker=dict(line=dict(width=1, color="white")))
    hist.add_shape(
    type="line",
    x0=val,
    x1=val,
    y0=0,
    y1=1,
    yref="paper",
    line=dict(color="red", width=2),
)
    hist.add_annotation(
        x=val+13,
        y=0.95,
        yref="paper",
        text=f"{country}: {val:.2f}",
        showarrow=False,
        font=dict(size=12, color="black"),
        borderpad=4,
    )
    hist.update_layout(yaxis_title="Count")

    
    if pathname == "/":
        return html.Div([
            html.H2(f"Map of {index} around the Globe", style={'textAlign': 'center'}),
            dcc.Graph(figure=map),
            html.Br(),
            html.P("*selected country shown in red triangle")
        ])
    elif pathname == "/page-1":
        return html.Div([
            html.H2(f"Histogram of {index}", style={'textAlign': 'center'}),
            dcc.Graph(figure=hist)
        ])
    
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

if __name__ == '__main__':
    app.run_server()
