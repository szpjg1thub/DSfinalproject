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

# Create dropdown options from actual launch sites + ALL
site_options = (
    [{'label': 'All Sites', 'value': 'ALL'}] +
    [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]
)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                  dcc.Dropdown(id='site-dropdown',  
                                               options=site_options, 
                                               value='All',
                                               placeholder='place holder here',
                                               searchable=True
                                               ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',                                                
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                value=[min_payload, max_payload],
                                                marks={
                                                    int(min_payload): str(int(min_payload)),
                                                    int((min_payload + max_payload) / 2): str(int((min_payload + max_payload) / 2)),
                                                    int(max_payload): str(int(max_payload))
                                                },
                                                allowCross=False
                                                ),

                                html.Br(),
                                                    

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        
        successes_by_site = (
            filtered_df.groupby('Launch Site', as_index=False)['class'].sum()
        )
        fig = px.pie(
            successes_by_site,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    else:
        # return the outcomes piechart for a selected site
        
       
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        # Count outcomes (class 1 vs 0)
        outcome_counts = (
            site_df['class']
            .value_counts()
            .rename_axis('class')
            .reset_index(name='count')
        )
        # Map to readable labels
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failed'})

        fig = px.pie(
            outcome_counts,
            values='count',
            names='Outcome',
            title=f'Launch Outcomes for {entered_site}'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    # Filter by payload range first
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    # Optional: narrow by selected site
    if entered_site is not None and entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Payload vs. Outcome for {entered_site} ({int(low)}–{int(high)} kg)'
    else:
        title = f'Payload vs. Outcome for All Sites ({int(low)}–{int(high)} kg)'

    # Scatter plot: payload vs success (class). Color by Booster Version Category if available
    color_col = 'Booster Version Category' if 'Booster Version Category' in filtered_df.columns else 'Launch Site'

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color=color_col,
        title=title,
        symbol='Launch Site'
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
