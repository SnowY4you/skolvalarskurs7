import pandas as pd
from tabulate import tabulate
import folium
from folium.plugins import Search
from geopy.distance import geodesic
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import streamlit as st
import socket

# Load the data file
file_path = 'School_choise.xlsm'
df = pd.read_excel(file_path)

# Set display option to show all columns
pd.set_option('display.max_columns', None)

# Convert columns to numeric, errors='coerce' will convert non-numeric values to NaN
df['Andel (%) elever behöriga till yrkesprog.'] = pd.to_numeric(df['Andel (%) elever behöriga till yrkesprog.'], errors='coerce')
df['Andel (%) elever behöriga till estetiskt program'] = pd.to_numeric(df['Andel (%) elever behöriga till estetiskt program'], errors='coerce')
df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'] = pd.to_numeric(df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'], errors='coerce')
df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'] = pd.to_numeric(df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'], errors='coerce')
df['Genomsnittligt meritvärde (17 ämnen)'] = pd.to_numeric(df['Genomsnittligt meritvärde (17 ämnen)'], errors='coerce')

# Calculate average scores
avg_yrkesprog = df['Andel (%) elever behöriga till yrkesprog.'].mean()
avg_estetiskt = df['Andel (%) elever behöriga till estetiskt program'].mean()
avg_nat_tech = df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'].mean()
avg_betyg = df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'].mean()
avg_merit = df['Genomsnittligt meritvärde (17 ämnen)'].mean()

# Define profile keywords
profile_keywords = ['Idrott', 'MA', 'NO', 'Fotboll', 'Språk', 'Kör', 'Dans', 'Konst/Design', 'Framtidsinriktning', 'Musik', 'Hem/Konsumentkunskap', 'Ingen', 'Entreprenörskap', 'Handboll', 'Internationalisering/språk', 'Innebandy', 'Spetsutbildning', 'Waldorf', 'SO', 'Ishockey', 'Konståkning', 'Simning', 'Multiidrott']

# Initiate Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = html.Div(
    style={'background': 'linear-gradient(to bottom, darkcyan, #6693f5)', 'color': 'white'},
    children=[
        html.Div(
            style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'},
            children=[
                html.Div(
                    id='filter_block',
                    children=[
                        html.Label(
                            'Välja en omdöme (man kan välja fler):',
                            style={'font-weight': 'bold', 'fontSize': 20, 'color': 'white'}
                        ),
                        dcc.Dropdown(
                            id='score_dropdown',
                            options=[
                                {'label': 'Andel (%) elever behöriga till yrkesprogram', 'value': 'avg_yrkesprog'},
                                {'label': 'Andel (%) elever behöriga till estetiskt program', 'value': 'avg_estetiskt'},
                                {'label': 'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program', 'value': 'avg_nat_tech'},
                                {'label': 'Andel (%) elever som uppfyllt betygskriterierna i alla ämnen', 'value': 'avg_betyg'},
                                {'label': 'Genomsnittligt meritvärde (17 ämnen)', 'value': 'avg_merit'}
                            ],
                            multi=True,
                            style={'color': 'black', 'fontSize': 20, 'backgroundColor': 'white'}
                        ),
                        html.Label(
                            'Profil (man kan välja fler):',
                            style={'font-weight': 'bold', 'fontSize': 20, 'color': 'white'}
                        ),
                        dcc.Dropdown(
                            id='profile_dropdown',
                            options=[{'label': keyword, 'value': keyword} for keyword in profile_keywords],
                            multi=True,
                            style={'color': 'black', 'fontSize': 20}
                        )
                    ],
                    style={'padding': '10px', 'backgroundColor': '#6693f5', 'width': '900px'}
                ),
                html.Div(
                    id='info_block',
                    children=[
                        html.H2('Val av skola inför årskurs 7'),
                        html.P('Här kan du kolla på grundskolar i Linköping och välja efter meritvärde, andel behöriga och profil. Informationen har hämtas från Skolverkets statistik 2023/2024.'),
                        html.P('Använd rullgardinsmenyerna för att välja olika värde och profiler för att filtrera skolorna. Tabellen och kartan kommer att uppdateras automatisk.'),

                    ],
                    style={'fontSize': 20, 'padding': '10px', 'backgroundColor': '#6693f5', 'width': 'calc(100% - 910px)', 'margin-left': '10px'}
                )
            ]
        ),
        html.Div(
            style={'display': 'flex'},
            children=[
                html.Div(
                    id='table_block',
                    children=[
                        dash_table.DataTable(
                            id='table',
                            columns=[{'name': col, 'id': col} for col in df.columns],
                            data=df.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': '#4868d3', 'color': 'white', 'text-align': 'center', 'fontWeight': 'bold', 'height': '80px', 'whiteSpace': 'normal'},
                            style_cell={'backgroundColor': 'white', 'color': '#020403', 'fontSize': 20, 'textAlign': 'center', 'border': '2px solid #696880'},
                            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#afdcec'}]
                        )
                    ],
                    style={'border': '2px solid #8e71dd', 'padding': '10px', 'width': '50%', 'height': '900px', 'overflowY': 'scroll'}
                ),
                html.Div(
                    id='visual_block',
                    children=[html.Iframe(id='map', style={'height': '1000px', 'width': '100%'})],
                    style={'border': '2px solid #0d98ba', 'backgroundColor': '#6693f5', 'padding': '10px', 'width': '50%', 'height': '900px', 'overflowY': 'scroll'}
                )
            ]
        )
    ]
)
# Helper function to rank schools based on multiple conditions
def assign_points(dataframe, num_points):
    points = {}
    for i, row in dataframe.iterrows():
        points[row['Skola']] = num_points - i
    return points


# Helper function to create the Folium map
def generate_map(home_coords, schools_df):
    m = folium.Map(location=home_coords, zoom_start=13, tiles='OpenStreetMap')

    # Add 'Home' marker with customized popup
    popup_html = """
    <div style="font-size: 18px; background-color: #e0d8f6; padding: 12px; border-radius: 4px;">
         Utgångspunkt:<br> 
        <b>Nya Rydskolan</b>
    </div>
    """
    popup = folium.Popup(popup_html, max_width=300)

    folium.Marker(location=home_coords, popup=popup, icon=folium.Icon(color='purple')).add_to(m)

    # Create a FeatureGroup for the schools
    school_markers = folium.FeatureGroup(name='Schools')

    # Add school markers with customized popups
    for i, row in schools_df.iterrows():
        school_coords = (row['Latitude'], row['Longitude'])
        distance = geodesic(home_coords, school_coords).km
        school_popup_html = f"""
        <div style="font-size: 18px; background-color: #d8dff6; padding: 12px; border-radius: 4px;">
            <b>{row['Skola']}</b><br>Distance: {distance:.2f} km
        </div>
        """
        school_popup = folium.Popup(school_popup_html, max_width=300)
        folium.Marker(
            location=school_coords,
            popup=school_popup,
            icon=folium.Icon(color='darkpurple')
        ).add_to(school_markers)

    # Add the FeatureGroup to the map
    school_markers.add_to(m)

    return m._repr_html_()


# Update the table and map based on the filter selection
@app.callback(
    Output('table', 'data'),
    Output('table', 'columns'),
    Output('map', 'srcDoc'),
    Input('score_dropdown', 'value'),
    Input('profile_dropdown', 'value')
)
def update_content(selected_scores, selected_profiles):
    filtered_df = df.copy()

    # Initialize map_html
    map_html = ""

    if selected_scores:
        for score in selected_scores:
            if score == 'avg_yrkesprog':
                filtered_df = filtered_df[filtered_df['Andel (%) elever behöriga till yrkesprog.'] >= avg_yrkesprog]
            elif score == 'avg_estetiskt':
                filtered_df = filtered_df[
                    filtered_df['Andel (%) elever behöriga till estetiskt program'] >= avg_estetiskt]
            elif score == 'avg_nat_tech':
                filtered_df = filtered_df[filtered_df[
                                              'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'] >= avg_nat_tech]
            elif score == 'avg_betyg':
                filtered_df = filtered_df[
                    filtered_df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'] >= avg_betyg]
            elif score == 'avg_merit':
                filtered_df = filtered_df[filtered_df['Genomsnittligt meritvärde (17 ämnen)'] >= avg_merit]

    if selected_profiles:
        profile_filter = filtered_df['Profil_Inriktning'].str.contains('|'.join(selected_profiles), case=False,
                                                                       na=False)
        filtered_df = filtered_df[profile_filter]

    # Filter out rows with NaN values in 'Latitude' and 'Longitude'
    filtered_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

    # Rank and sort schools
    total_points = {}
    for school in set(filtered_df['Skola']):
        total_points[school] = (assign_points(filtered_df[filtered_df['Skola'] == school], 9).get(school, 0))

    total_points_df = pd.DataFrame(list(total_points.items()), columns=['Skola', 'Total Points'])
    total_points_df = total_points_df.merge(filtered_df[['Skola', 'Typ av huvudman', 'elev_år',
                                                         'Andel (%) elever behöriga till yrkesprog.',
                                                         'Andel (%) elever behöriga till estetiskt program',
                                                         'Andel (%) elever behöriga till Ekonomi-, humanistiska och samhällsvetenskaps- program',
                                                         'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program',
                                                         'Andel (%) elever som uppfyllt betygskriterierna i alla ämnen',
                                                         'Genomsnittligt meritvärde (17 ämnen)', 'Profil_Inriktning',
                                                         'Ovrigt', 'Finns_Gymnasiumskolan','Latitude',
                                                         'Longitude']], on='Skola')
    sorted_schools = total_points_df.sort_values(by='Total Points', ascending=False)

    # Define columns to display
    columns_to_display = ['Skola', 'Typ av huvudman', 'elev_år', 'Andel (%) elever behöriga till yrkesprog.',
                          'Andel (%) elever behöriga till estetiskt program',
                          'Andel (%) elever behöriga till Ekonomi-, humanistiska och samhällsvetenskaps- program',
                          'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program',
                          'Andel (%) elever som uppfyllt betygskriterierna i alla ämnen',
                          'Genomsnittligt meritvärde (17 ämnen)', 'Profil_Inriktning', 'Ovrigt',
                          'Finns_Gymnasiumskolan']

    # Generate Folium Map
    home_coords = (58.410107, 15.565374)  # 'Nya Rydskolan'
    map_html = generate_map(home_coords, sorted_schools)

    # Prepare columns for the table
    table_columns = [{'name': col, 'id': col} for col in columns_to_display]

    return sorted_schools[columns_to_display].to_dict('records'), table_columns, map_html


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

