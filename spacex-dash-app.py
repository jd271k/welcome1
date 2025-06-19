# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Extract unique launch sites for dropdown options
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',  # ID für Callback-Referenz
        options=[{'label': 'Alle Startplätze', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in launch_sites],  # Options mit ALL + Startplätzen
        value='ALL',  # Standardwert: Alle Startplätze
        placeholder="Wählen Sie hier einen Startplatz aus",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]  # Standardwerte auf min und max gesetzt
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Gesamterfolg aller Standorte - Tortendiagramm der erfolgreichen Starts
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Erfolgreiche Starts pro Startplatz (Alle Startplätze)'
        )
        return fig
    else:
        # Filter nach ausgewähltem Startplatz
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Zähle Erfolge (class=1) und Misserfolge (class=0)
        success_fail_counts = filtered_df['class'].value_counts().rename_axis('class').reset_index(name='counts')
        # Tortendiagramm für Erfolg vs Misserfolg an dem ausgewählten Startplatz
        fig = px.pie(
            success_fail_counts,
            names='class',
            values='counts',
            title=f'Erfolgsquote für {entered_site}',
            labels={'class': 'Erfolg (1) / Misserfolg (0)'}
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter nach Payload-Mass (kg)
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        # Scatter Plot aller Standorte im Payload-Bereich
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Erfolg für alle Startplätze',
            labels={'class': 'Erfolg (1) / Misserfolg (0)'}
        )
        return fig
    else:
        # Scatter Plot für spezifischen Startplatz
        filtered_df_site = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df_site, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Erfolg für {entered_site}',
            labels={'class': 'Erfolg (1) / Misserfolg (0)'}
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
