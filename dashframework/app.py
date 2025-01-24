from dash import Dash, html, dcc
import dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import os
from urllib.request import urlopen
import json
from us import states
from datetime import datetime

from jbi100_app.data import preprocess_data, group_by_state, visualize_state_map, bin_columns
from jbi100_app.config import DATA_PATH
from jbi100_app.main import app

import plotly.express as px
import dash
from dash.dependencies import Input, Output, State
import dash_leaflet as dl 

from urllib.request import urlopen
import json
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Base directory for your data files
# base_dir = r'C:\Users\emmaw\Documents\uni NL\y2\Visualisation\dashframework\Work-related Injury and Illness'
# file_name = 'ITA Case Detail Data 2023 through 8-31-2023.csv'
# csv_file_path = os.path.join(base_dir, file_name)


# Preprocess the data
df = preprocess_data(DATA_PATH)

# Bin numerical and date columns
df.loc[:,'djtr_num_tr_binned'] = pd.cut(df['djtr_num_tr'], 
                                  bins=[0, 40, 80, 120, 180, df['djtr_num_tr'].max() + 1], 
                                  labels=['0-40', '41-80', '81-120', '121-180', '181+'], right=False)
df.loc[:,'dafw_num_away_binned'] = pd.cut(df['dafw_num_away'], 
                                    bins=[0, 5, 10, 20, 50, 100, df['dafw_num_away'].max() + 1], 
                                    labels=['0-5', '6-10', '11-20', '21-50', '51-100', '100+'], right=False)
df.loc[:,'annual_average_employees_binned'] = pd.cut(df['annual_average_employees'], 
                                                bins=[0, 10, 50, 100, 500, 1000, df['annual_average_employees'].max() + 1], 
                                                labels=['0-10', '11-50', '51-100', '101-500', '501-1000', '1000+'], right=False)
df.loc[:,'total_hours_worked_binned'] = pd.cut(df['total_hours_worked'], 
                                         bins=[0, 20000, 50000, 100000, 200000, df['total_hours_worked'].max() + 1], 
                                         labels=['0-20k', '20k-50k', '50k-100k', '100k-200k', '200k+'], right=False)
df.loc[:,'date_of_incident_binned'] = pd.to_datetime(df['date_of_incident']).dt.to_period('M').astype(str)

# Initialize the Dash app
app = Dash(__name__)
app.title = "Work-Related Injuries Dashboard"



# Load the GeoJSON data for counties
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)



state_counts = group_by_state(df)
fig = visualize_state_map(state_counts)



# Helter dictionaries to rename dropdown buttons
establishment_type_lookup = {
    "Private Industry": "1.0",
    "State Government Entity": "2.0",
    "Local Government Entity": "3.0"
}
establishment_type_lookup_r = {v: k for k, v in establishment_type_lookup.items()}


size_lookup = {
    "< 20 employees": "1",
    "20 - 99 employees": "21",
    "100 - 249 employees": "22",
    "20 - 249 employees": "2",
    "250+ employees": "3"
}
size_lookup_r = {v: k for k, v in size_lookup.items()}


type_of_incident_lookup = {
    "Injury": "1",
    "Skin Disorder": "2",
    "Respiratory Condition": "3",
    "Poisoning": "4",
    "Hearing Loss": "5",
    "All Other Illness": "6"
}
type_of_incident_lookup_r = {v: k for k, v in type_of_incident_lookup.items()}


incident_outcome_lookup = {
    "Death": "1",
    "Days Aways From Work": "2",
    "Job Transfer or Restriction": "3",
    "Other Recordable Case": "4"
}
incident_outcome_lookup_r = {v: k for k, v in incident_outcome_lookup.items()}




# Define layout
app.layout = html.Div([
    html.H1("Work-Related Injuries Dashboard", style={'text-align': 'center'}),
    html.Div([
        # Filters
        html.Div([
            html.H2("Filters", style={'text-align': 'left'}),
            html.Div([
                html.Label('State', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[{'label': i, 'value': i} for i in ['All'] + sorted(df['state'].unique())],
                    value='All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Establishment Type', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='establishment-type-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All'] + list(establishment_type_lookup.keys())],
                    value='All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Size', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='size-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All'] + list(size_lookup.keys())],
                    value='All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Type of Incident', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='type-of-incident-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All'] + list(type_of_incident_lookup.keys())],
                    value='All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Days Away from Work', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='dafw-num-away-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All', '0-5', '6-10', '11-20', '21-50', '51-100', '100+']],
                    value='All', clearable=False
                ),
            ]),
            html.Div([
                html.Label('Annual Average Employees', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='annual_average_employees-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All', '0-10', '11-50', '51-100', '101-500', '501-1000', '1000+']],
                    value='All', clearable=False
                ),
            ]),
            html.Div([
                html.Label('Total Hours Worked', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='total_hours_worked-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All', '0-20k', '20k-50k', '50k-100k', '100k-200k', '200k+']],
                    value='All', clearable=False
                ),
            ]),
            html.Div([
                html.Label('Incident Outcome', style={'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='incident_outcome-dropdown',
                    options=[{'label': label, 'value': label} for label in ['All'] + list(incident_outcome_lookup.keys())],
                    value='All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Days of Job Transfer/Restriction', style = {'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id = 'djtr_num_tr-dropdown',
                    options = [{'label': label, 'value': label} for label in ['All'] + ['0-40', '41-80', '81-120', '121-180', '181+']],
                    value = 'All', clearable=False
                )
            ]),
            html.Div([
                html.Label('Date of Incident', style = {'display': 'block', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='date_of_incident-dropdown',
                    options = [{'label': label, 'value': label} for label in ['All'] + sorted(df.loc[:,'date_of_incident_binned'].unique().tolist())],
                    value='All', clearable=False
                )
            ]),

            html.Button('Reset Filters', id='reset-filters-button', n_clicks=0, style={
                                    "margin": "20px auto",
                                    "width": "100%",
                                    "padding": '14px 80px',
                                    "alignItems": "center",
                                    "backgroundColor": "#A52A2A",  # Red close button
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "5px",
                                    "cursor": "pointer"
                                }),
            
            # Reset Filters Button
            
        ], style={'width': '20%', 'background-color': '#f7f7f7', 'padding': '20px', 'position': 'fixed', 'right': '0', 'top': '0', 'height': '100vh', 'overflow-y': 'auto'}),




        
        # Choropleth map
        html.Div("Occurences by state", style={'text-align': 'left', 'font-size': '25px'}),
        html.Div([
            dcc.Graph(id='choropleth-map', style={'width': '75%', 'height': '50%', 'margin': 'auto'}),
            html.Div(
                id="modal",
                style={
                    "display": "none",  # Initially hidden
                    "position": "center",
                    "top": "15%",  # Position the modal 10% from the top of the screen
                    "left": "15%",  # Position the modal 25% from the left of the screen
                    "width": "50%",  # Adjust modal width
                    "height": "70%",  # Adjust modal height
                    "backgroundColor": "rgba(0, 0, 0, 0.5)",
                    "zIndex": "1000",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "paddingBottom": "80px"
                },
                children=[
                    html.Div(
                        style={
                            "backgroundColor": "#f0f8ff",  # Light blue background
                            "padding": "20px",
                            "borderRadius": "10px",  # Rounded corners
                            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",  # Add shadow for better appearance
                            "width": "100%",  # Use full modal width
                            "height": "100%",  # Use full modal height
                            "textAlign": "center",
                        },
                        children=[
                            dcc.Graph(id="modal-graph"),
                            html.Button(
                                "Close", 
                                id="close-button",
                                style={
                                    "marginTop": "5px",
                                    "padding": "10px 20px",
                                    "backgroundColor": "#A52A2A",  # Red close button
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "5px",
                                    "cursor": "pointer",
                                }
                            ),
                        ]
                    )
                ],
            ),
        ], style={'display': 'flex', 'justify-content': 'center'}),


        # Bar Chart
        html.Div([
            html.Div("Distribution per / of:", style={'text-align': 'left', 'font-size': '25px'}),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[
                    {'label': 'State', 'value': 'state'},
                    {'label': 'Establishment Type', 'value': 'establishment_type'},
                    {'label': 'Size', 'value': 'size'},
                    {'label': 'Type of Incident', 'value': 'type_of_incident'},
                    {'label': 'Days Away from Work', 'value': 'dafw_num_away'},
                    {'label': 'Annual Average Employees', 'value': 'annual_average_employees'},
                    {'label': 'Total Hours Worked', 'value': 'total_hours_worked'},
                    {'label': 'Incident Outcome', 'value': 'incident_outcome'},
                    {'label': 'Days of Job Transfer/Restriction', 'value': 'djtr_num_tr'},
                    {'label': 'Date of Incident', 'value': 'date_of_incident'}
                ],
                value='state', 
                clearable=False,
                style={"width": "25vh", "margin-left":"5vh" }
            ),
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px'}),
        dcc.Graph(id='bar-chart', clickData=None,
                  style={'height':'30vh','width':'100%', 'display': 'inline-block'})

    ], style={'width': '75%', 'height': '10%', 'display':'block', 'margin-right': '10px'}),  # Left side content 

])



@app.callback(
    [
        Output('bar-chart', 'figure'),
        Output('choropleth-map', 'figure'),
        Output('state-dropdown', 'value'),
        Output('establishment-type-dropdown', 'value'),
        Output('size-dropdown', 'value'),
        Output('type-of-incident-dropdown', 'value'),
        Output('dafw-num-away-dropdown', 'value'),
        Output('annual_average_employees-dropdown', 'value'),
        Output('total_hours_worked-dropdown', 'value'),
        Output('incident_outcome-dropdown', 'value'),
        Output('djtr_num_tr-dropdown', 'value'),
        Output('date_of_incident-dropdown', 'value'),
        
    ],
    [
        Input('state-dropdown', 'value'),
        Input('establishment-type-dropdown', 'value'),
        Input('size-dropdown', 'value'),
        Input('type-of-incident-dropdown', 'value'),
        Input('dafw-num-away-dropdown', 'value'),
        Input('annual_average_employees-dropdown', 'value'),
        Input('total_hours_worked-dropdown', 'value'),
        Input('incident_outcome-dropdown', 'value'),
        Input('djtr_num_tr-dropdown', 'value'),
        Input('date_of_incident-dropdown', 'value'),
        Input('reset-filters-button', 'n_clicks'),
        Input('variable-dropdown', 'value'),
        Input('bar-chart', 'clickData'),
        Input('choropleth-map', 'clickData')
    ]
)
def update_primary(state, establishment_type, size, type_of_incident, dafw_num_away, 
                   annual_average_employees, total_hours_worked, incident_outcome, 
                   selected_djtr_bin, date_of_incident, reset_clicks, selected_variable, bar_clickData, map_clickData):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    filtered_df = df.copy()
    # Check if the reset button is clicked
    if triggered_id == 'reset-filters-button':
        state = 'All'
        establishment_type = 'All'
        size = 'All'
        type_of_incident = 'All'
        dafw_num_away = 'All'
        annual_average_employees = 'All'
        total_hours_worked = 'All'
        incident_outcome = 'All'
        selected_djtr_bin = 'All'
        date_of_incident = 'All'

    # Update dropdown values based on bar-chart clicks
    if triggered_id == 'bar-chart' and bar_clickData:
        clicked_value = bar_clickData['points'][0]['x']
        if selected_variable == 'state':
            state = clicked_value
        elif selected_variable == 'establishment_type':
            establishment_type = establishment_type_lookup_r[clicked_value]
        elif selected_variable == 'size':
            size = size_lookup_r[clicked_value]
        elif selected_variable == 'type_of_incident':
            type_of_incident = type_of_incident_lookup_r[clicked_value]
        elif selected_variable == 'dafw_num_away':
            dafw_num_away = clicked_value
        elif selected_variable == 'annual_average_employees':
            annual_average_employees = clicked_value
        elif selected_variable == 'total_hours_worked':
            total_hours_worked = clicked_value
        elif selected_variable == 'incident_outcome':
            incident_outcome = incident_outcome_lookup_r[clicked_value]
        elif selected_variable == 'djtr_num_tr':
            selected_djtr_bin = clicked_value
        elif selected_variable == 'date_of_incident':
            date_of_incident = datetime.strptime(clicked_value, "%Y-%m-%d").strftime("%Y-%m")

    # Filter data
    if state != 'All':
        filtered_df = filtered_df[filtered_df['state'] == state]
    if establishment_type != 'All':
        filtered_df = filtered_df[filtered_df['establishment_type'] == establishment_type_lookup[establishment_type]]
    if size != 'All':
        filtered_df = filtered_df[filtered_df['size'] == size_lookup[size]]
    if type_of_incident != 'All':
        filtered_df = filtered_df[filtered_df['type_of_incident'] == type_of_incident_lookup[type_of_incident]]
    if dafw_num_away != 'All':
        filtered_df = filtered_df[filtered_df['dafw_num_away_binned'] == dafw_num_away]
    if annual_average_employees != 'All':
        filtered_df = filtered_df[filtered_df['annual_average_employees_binned'] == annual_average_employees]
    if total_hours_worked != 'All':
        filtered_df = filtered_df[filtered_df['total_hours_worked_binned'] == total_hours_worked]
    if incident_outcome != 'All':
        filtered_df = filtered_df[filtered_df['incident_outcome'] == incident_outcome_lookup[incident_outcome]]
    if selected_djtr_bin != 'All':
        filtered_df = filtered_df[filtered_df['djtr_num_tr_binned'] == selected_djtr_bin]
    if date_of_incident != 'All':
        filtered_df = filtered_df[filtered_df['date_of_incident_binned'] == date_of_incident]

    
    # Update state dropdown value when clicking on the map
    if triggered_id == 'choropleth-map' and map_clickData:
        state = map_clickData['points'][0]['location']


        # Filter data
        if state != 'All':
            filtered_df = filtered_df[filtered_df['state'] == state]
        if establishment_type != 'All':
            filtered_df = filtered_df[filtered_df['establishment_type'] == establishment_type_lookup[establishment_type]]
        if size != 'All':
            filtered_df = filtered_df[filtered_df['size'] == size_lookup[size]]
        if type_of_incident != 'All':
            filtered_df = filtered_df[filtered_df['type_of_incident'] == type_of_incident_lookup[type_of_incident]]
        if dafw_num_away != 'All':
            filtered_df = filtered_df[filtered_df['dafw_num_away_binned'] == dafw_num_away]
        if annual_average_employees != 'All':
            filtered_df = filtered_df[filtered_df['annual_average_employees_binned'] == annual_average_employees]
        if total_hours_worked != 'All':
            filtered_df = filtered_df[filtered_df['total_hours_worked_binned'] == total_hours_worked]
        if incident_outcome != 'All':
            filtered_df = filtered_df[filtered_df['incident_outcome'] == incident_outcome_lookup[incident_outcome]]
        if selected_djtr_bin != 'All':
            filtered_df = filtered_df[filtered_df['djtr_num_tr_binned'] == selected_djtr_bin]
        if date_of_incident != 'All':
            filtered_df = filtered_df[filtered_df['date_of_incident_binned'] == date_of_incident]


    # Create bins and grouping for bar chart
    grouped_data = df.copy()
    if selected_variable in ['dafw_num_away', 'djtr_num_tr', 'annual_average_employees', 'total_hours_worked', 'date_of_incident']:
        grouped_data = filtered_df[f'{selected_variable}_binned'].value_counts().sort_index().reset_index()
        grouped_data.columns = [selected_variable, 'Count']
    else:
        grouped_data = filtered_df[selected_variable].value_counts().reset_index()
        grouped_data.columns = [selected_variable, 'Count']


    bar_fig = px.bar(grouped_data, x=selected_variable, y='Count')
    bar_fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20)
    )

    if selected_variable == "type_of_incident":

        bar_fig.update_xaxes(
            
            ticktext=list(type_of_incident_lookup_r.values()),  # Use the reversed labels
            tickvals=list(type_of_incident_lookup_r.keys())    # Use the original keys
        )
    elif selected_variable == 'size':
        bar_fig.update_xaxes(
        categoryorder='array', 
        categoryarray=["1", "2", "21", "22", "3"],  # The order of the categories
        ticktext=["< 20", "20 - 99", "100 - 249", "20 - 249", "250+"],  # Custom display labels
        tickvals=["1", "21", "22", "2", "3"]  # Corresponding x-values
    )
 
       
    elif selected_variable == 'establishment_type':
            bar_fig.update_xaxes(
                
                ticktext=list(establishment_type_lookup_r.values()),  # Use the reversed labels
                tickvals=list(establishment_type_lookup_r.keys())    # Use the original keys
            )
    elif selected_variable == 'incident_outcome':
            bar_fig.update_xaxes(
                
                ticktext=list(incident_outcome_lookup_r.values()),  # Use the reversed labels
                tickvals=list(incident_outcome_lookup_r.keys())    # Use the original keys
            )
    # Create choropleth map
    state_counts_filtered = group_by_state(filtered_df)
    map_fig = visualize_state_map(state_counts_filtered)
    map_fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return bar_fig, map_fig, state, establishment_type, size, type_of_incident, dafw_num_away, annual_average_employees, total_hours_worked, incident_outcome, selected_djtr_bin, date_of_incident




# Callbackas for popup window
@app.callback(
    [Output("modal", "style"), Output("modal-graph", "figure")],
    [Input("choropleth-map", "clickData"), Input("close-button", "n_clicks")],
    prevent_initial_call="both",
)
def toggle_modal(clickData, n_clicks):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered == "choropleth-map" and clickData:
        state = clickData["points"][0]["location"]
        state_data = df[df["state"] == state]

        scatter_matrix_figure = px.scatter_matrix(
            state_data,
            dimensions=["annual_average_employees", "size", "dafw_num_away", "total_hours_worked", "djtr_num_tr"],
            color="type_of_incident",
            symbol="type_of_incident",
            title=f"Multivariate Analysis for {state}",
            labels={
                "annual_average_employees": "Avg Employees",
                "size": "Size",
                "dafw_num_away": "Not at Work",
                "total_hours_worked": "Tot Hours",
                "djtr_num_tr": "Job Transfer"
            }
        )
        scatter_matrix_figure.update_traces(diagonal_visible=False)
        scatter_matrix_figure.update_layout(
            autosize=True, showlegend=True, width=850, height=620
        )
        return {
            "display": "block",
            "position": "fixed",
            "top": "10%",
            "left": "25%",
            "width": "50%",
            "height": "70%",
            "backgroundColor": "rgba(0, 0, 0, 0.5)",
            "zIndex": "1000",
            "justifyContent": "center",
            "alignItems": "center",
        }, scatter_matrix_figure

    if triggered == "close-button":
        return {"display": "none"}, dash.no_update

    return dash.no_update, dash.no_update



if __name__ == '__main__':
    app.run_server(debug=True, port=8052)