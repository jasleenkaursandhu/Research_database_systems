import dash
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_color_picker
from dash import dcc, html, Input, Output, State, ALL, callback
from mongodb_utils import fetch_mongodb_faculty_data, get_top_keywords_by_year_range
from neo4j_utils import fetch_top_professors_for_keyword, get_university_keyword_scores
from mysql_utils import fetch_faculty_data, fetch_all_keywords, fetch_all_university_names, get_publications_by_ids
from mysql_utils import fetch_top_universities_for_keyword, fetch_universities_with_most_faculty
from mysql_utils import fetch_all_research_interests, add_research_interest_with_procedure, delete_research_interest

# Fetch all faculty data from MySQL Utils
faculty_data = fetch_faculty_data()

# Fetch all keywords from MySQL Utils
all_keywords = fetch_all_keywords()

# Fetch all university names from MySQL Utils
all_universities = fetch_all_university_names() 

# Create Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define styles
colors = {
    'background': '#ECDCEE',
    'text': '#4F2D58',
    'card_background': 'white',
    'card_border': '1px #6E1279',
    'dropdown_border': '1px solid grey',
    'dropdown_bg': 'white',
    'dropdown_text': 'black'
}

# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '30px'}, children=[
    # html.H1('Research Collaboration Navigator for Prospective Grad Students', style={'color': colors['text'],'textAlign': 'center'}),
    html.H1("Research Interests Wayfinder", style={'color': colors['text'],'textAlign': 'center'}),
    html.P("A Prospective Student's Guide to Academic Exploration", style={'color': colors['text'],'textAlign': 'center'}),

    ## First Row - Widgets 1 and 2
    dbc.Row([
        dbc.Col([
            html.Div(style={'backgroundColor': colors['card_background'], 'border': colors['card_border'], 'padding': '20px', 'margin': '20px 0', 'border-radius': '10px'}, children=[
                html.H2('Select a faculty member to view their profile', style={'color': colors['text']}),
                html.Label('Select a faculty member:', style={'color': colors['text']}),
                dcc.Dropdown(
                    id='faculty-dropdown',
                    options=[{'label': row[1], 'value': row[0]} for row in faculty_data],
                    style={'border': colors['dropdown_border'], 'backgroundColor': colors['dropdown_bg'], 'color': colors['dropdown_text']}
                ),
                html.Div(id='faculty-info-output', style={'backgroundColor': colors['card_background'], 'border': colors['card_border'], 'padding': '20px', 'margin': '20px 0', 'border-radius': '10px'})
            ])
        ], width=6),

        dbc.Col([
            html.Div(style={'backgroundColor': colors['card_background'], 'border': colors['card_border'], 'padding': '20px', 'margin': '20px 0', 'border-radius': '10px'}, children=[
                html.H2('Top Keywords in Publications Through the Years', style={'color': colors['text']}),
                dcc.RangeSlider(
                    id='year-range-slider',
                    min=1982,
                    max=2023,
                    step=1,
                    marks={year: str(year) for year in range(1982, 2024, 2)},
                    value=[2010, 2020]
                ),
                html.Div(
                    id='top-keywords-output',
                    style={
                        'backgroundColor': colors['card_background'],
                        'border': colors['card_border'],
                        'padding': '20px',
                        'margin': '20px 0',
                        'border-radius': '10px'
                    }
                )
            ])
        ], width=6)
    ]),

    ## Second Row - Widgets 3 and 4
    dbc.Row([
        dbc.Col([
            html.Div(style={'backgroundColor': colors['card_background'], 'border': colors['card_border'], 'padding': '20px', 'margin': '20px 0', 'border-radius': '10px'}, children=[
                html.H2('Top Universities for Keyword by Faculty Members Count', style={'color': colors['text']}),
                html.Label('Select a Keyword:', style={'color': colors['text']}),
                dcc.Dropdown(
                    id='keyword-dropdown',
                    options=[{'label': row[1], 'value': row[1]} for row in all_keywords],
                    placeholder='Select a Keyword',
                    style={'width': '100%', 'margin-top': '10px'}
                ),
                dcc.Graph(id='universities-faculty-sunburst-chart')
            ])
        ], width=6),

        dbc.Col([
            html.Div(style={'backgroundColor': colors['card_background'], 'border': colors['card_border'], 'padding': '20px', 'margin': '20px 0', 'border-radius': '10px'}, children=[
                html.H2('Top Keywords for University by Keyword Relevant Citation Score (KRC)', style={'color': colors['text']}),
                html.Label('Select a University:', style={'color': colors['text']}),
                dcc.Dropdown(
                    id='university-dropdown',
                    options=[{'label': name, 'value': name} for name in all_universities],
                    placeholder='Select a University',
                    style={'width': '100%', 'margin-top': '10px'}
                ),
                dcc.Graph(id='keyword-scores-bar-chart'),
                dash_color_picker.ColorPicker(id='ColorPicker', color='#872367')
            ])
        ], width=6)
    ]),

    ## Third Row - Widgets 5 and 6
    dbc.Row([
        ## Add/Delete research interests dropdowns ##
        dbc.Col([
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.H2('Add/Delete Research Interests', style={'color': colors['text']}),
                html.Div([
                    html.Label('Select a research interest to add:', style={'color': colors['text']}),
                    dcc.Dropdown(
                        id='add-research-interest-input',
                        options=[{'label': row[1], 'value': row[1]} for row in all_keywords],
                        placeholder='Select a keyword from dropdown',
                        style={'width': '100%', 'margin-top': '10px'}
                    ),
                    html.Button(
                        'Add Keyword',
                        id='add-keyword-button',
                        n_clicks=0,
                        style={'margin-top': '10px', 'width': '100%'}
                    )
                ]),
                html.Div([
                    html.Label('Select a research interest to delete:', style={'color': colors['text']}),
                    dcc.Dropdown(
                        id='delete-research-interest',
                        options=[{'label': row[1], 'value': row[1]} for row in all_keywords],
                        placeholder='Select a keyword from dropdown',
                        style={'width': '100%', 'margin-top': '20px'}
                    ),
                    html.Button(
                        'Delete Keyword',
                        id='delete-keyword-button',
                        n_clicks=0,
                        style={'margin-top': '10px', 'width': '100%'}
                    )
                ]),
                html.Div(
                    id='keyword-operation-feedback',
                    style={'margin-top': '10px'}
                ),
                dcc.Location(id='url', refresh=False),
            ])
        ], width=6),

        ## List of Research Interests ##
        dbc.Col([
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.H2('List of User Research Interests', style={'color': colors['text']}),
                html.Table(
                    id='research-interests-table',
                    style={'width': '100%', 'margin-top': '10px'}
                )
            ])
        ], width=6)
    ]),

    ## Fourth Row - Widgets 7 and 8
    dbc.Row([
        ## Professors Output ##
        dbc.Col([
            html.Div(id='professors-output')
        ], width=6),

        ## Universities Output ##
        dbc.Col([
            html.Div(id='universities-output')
        ], width=6)
    ])
])

## Widget 1: Retrieves Faculty Information Based on Selected Faculty Member from MongoDB
@app.callback(
    Output('faculty-info-output', 'children'),
    [Input('faculty-dropdown', 'value')]
)
def update_faculty_info(selected_faculty_id):
    """
    Callback to update the faculty information output based on the selected faculty member.

    This callback listens for changes in the selected faculty member from the dropdown.
    It fetches MongoDB data for the selected faculty member and extracts various data fields
    such as name, position, research interests, email, phone, affiliation, photo URL, and keywords.
    It generates HTML to display the faculty information, including the name, position, affiliation,
    photo, and a list of keywords associated with the faculty member.

    Parameters:
    - selected_faculty_id (str): The ID of the selected faculty member from the dropdown.

    Returns:
    - faculty_info (dash.html.Div): The HTML component displaying the faculty information.
    """
    # Fetch MongoDB data for the selected faculty member
    selected_faculty_info = fetch_mongodb_faculty_data(selected_faculty_id)

    # Check if selected_faculty_info is empty
    if not selected_faculty_info:
        return "Faculty data not found.", []

    # Extracting individual data fields
    name = selected_faculty_info.get('name', '')
    position = selected_faculty_info.get('position', '')
    research_interest = selected_faculty_info.get('researchInterest', '')
    email = selected_faculty_info.get('email', '')
    phone = selected_faculty_info.get('phone', '')
    affiliation = selected_faculty_info.get('affiliation', {})
    affiliation_name = affiliation.get('name', '') if affiliation else ''
    photo_url = selected_faculty_info.get('photoUrl', '')
    keywords = selected_faculty_info.get('keywords', [])
    publication_ids = selected_faculty_info.get('publication_ids', [])  # Retrieve publication IDs
    publications = get_publications_by_ids(publication_ids)

    # Generate HTML to display faculty info
    faculty_info = html.Div([
        html.Div([
            html.P(f"Name: {name}", className='mb-1'),
            html.P(f"Position: {position}", className='mb-1'),
            html.P(f"Affiliation: {affiliation_name}", className='mb-1'),
            html.Img(src=photo_url, alt=name, style={'width': '200px', 'height': 'auto'}),
        ], className='d-flex justify-content-center mb-3'),

        html.Div([
            html.Hr(),
            # Check if email is not None or empty
            html.P(f"Email: {email}", className='mb-1') if email else None,
            # Check if phone is not None or empty
            html.P(f"Phone: {phone}", className='mb-1') if phone else None,
            html.Hr(),
            html.A("Associated Keywords", id="keywords-title", className='mb-1', style={'textDecoration': 'underline', 'cursor': 'pointer'}),
            html.Div(id="keywords-div", children=[
                html.Ul([html.Li(keyword, className='mb-1') for keyword in keywords])
            ], className='mb-3', style={'display': 'none'}),  # Initially hide the keywords
            # Move "Associated Publications" hyperlink here
            html.P(html.A("Associated Publications", id="publications-title", className='mb-1', style={'textDecoration': 'underline', 'cursor': 'pointer'})),
            # Display publications in a table format
            html.Div(id="publications-div", children=[
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Title", style={'border': '1px solid #ddd', 'padding': '8px'}),
                            html.Th("Venue", style={'border': '1px solid #ddd', 'padding': '8px'}),
                            html.Th("Year", style={'border': '1px solid #ddd', 'padding': '8px'}),
                            html.Th("Citations", style={'border': '1px solid #ddd', 'padding': '8px'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(publication[1], style={'border': '1px solid #ddd', 'padding': '8px'}),  # Title
                            html.Td(publication[2], style={'border': '1px solid #ddd', 'padding': '8px'}),  # Venue
                            html.Td(publication[3], style={'border': '1px solid #ddd', 'padding': '8px'}),  # Year
                            html.Td(publication[4], style={'border': '1px solid #ddd', 'padding': '8px'})   # No. of Citations
                        ]) for publication in publications
                    ])
                ], style={'borderCollapse': 'collapse', 'border': '1px solid #ddd', 'width': '100%', 'marginBottom': '20px'})
            ], className='mb-3', style={'display': 'none'}) if publications else None # Initially hide the publications
        ], style={'color': colors['text']}),
    ], className='container')

    return faculty_info

## Callback to toggle visibility of keywords when the title is clicked
@app.callback(
    Output('keywords-div', 'style'),
    [Input('keywords-title', 'n_clicks')]
)
def toggle_keywords_visibility(n_clicks):
    """
    Callback to toggle the visibility of keywords when the title is clicked.

    This callback listens for clicks on the 'Keywords' title and toggles the visibility
    of the keywords display accordingly.

    Parameters:
    - n_clicks (int): Number of clicks on the 'Keywords' title.

    Returns:
    - style (dict): CSS style to control the visibility of the keywords display.
    """
    if n_clicks is not None and n_clicks % 2 == 1:
        return {'display': 'block'}  # Show the keywords
    else:
        return {'display': 'none'}   # Hide the keywords

## Callback to toggle visibility of publications when the title is clicked
@app.callback(
    Output('publications-div', 'style'),
    [Input('publications-title', 'n_clicks')]
)
def toggle_publications_visibility(n_clicks):
    """
    Callback to toggle the visibility of publications when the title is clicked.

    This callback listens for clicks on the 'Associated Publications' title and toggles the visibility
    of the publications display accordingly.

    Parameters:
    - n_clicks (int): Number of clicks on the 'Associated Publications' title.

    Returns:
    - style (dict): CSS style to control the visibility of the publications display.
    """
    if n_clicks is not None and n_clicks % 2 == 1:
        return {'display': 'block'}  # Show the publications
    else:
        return {'display': 'none'}   # Hide the publications

## Widget 2: Retrieves Top Keywords Output Based on Selected Year Range input by User from neo4j
@app.callback(
    Output('top-keywords-output', 'children'),
    [Input('year-range-slider', 'value')]
)
def update_top_keywords_output(year_range):
    """
    Callback to update the top popular keywords output by publications based on the selected year range.

    This callback listens for changes in the selected year range from the slider.
    It fetches the top keywords and their respective counts within the selected year range.
    Then, it constructs a list of HTML table rows, each containing a keyword and its count.
    If data is available, it returns a div containing a header ('Top Keywords') and the constructed table.
    If no data is available, it returns a div with a message indicating no data.

    Parameters:
    - year_range (tuple): A tuple containing the start and end years of the selected range.

    Returns:
    - children (dash.development.base_component.Component): The children components to be displayed.
    """
    top_keywords = get_top_keywords_by_year_range(year_range)
    if top_keywords:
        keyword_list = [
            html.Tr([
                html.Th('Keyword', style={'color': colors['text'], 'border': '1px solid black', 'padding': '8px'}),
                html.Th('Count', style={'color': colors['text'], 'border': '1px solid black', 'padding': '8px'})
            ])
        ]
        for i, keyword in enumerate(top_keywords):
            bg_color = '#FADADD' if i % 2 == 0 else 'inherit'
            keyword_list.append(
                html.Tr([
                    html.Td(keyword['keyword'], style={'color': colors['text'], 'border': '1px solid black', 'padding': '8px', 'background-color': bg_color}),
                    html.Td(keyword['count'], style={'color': colors['text'], 'border': '1px solid black', 'padding': '8px', 'background-color': bg_color})
                ])
            )
        return html.Div([
            html.H3('Top Keywords:', style={'color': colors['text']}),
            html.Table(
                keyword_list,
                style={'width': '100%', 'border-collapse': 'collapse', 'border-spacing': '0'}
            )
        ])
    else:
        return html.Div("No data available", style={'color': 'red'})

# Widget 3: Retrieves Top Universities Sunburst Chart Based on Selected Keyword and Count of Faculty Associated from MySQL
@app.callback(
    Output('universities-faculty-sunburst-chart', 'figure'),
    [Input('keyword-dropdown', 'value')]
)
def update_universities_faculty_pie_chart(keyword):
    """
    Callback to update the sunburst chart based on the selected keyword.

    This callback listens for changes in the selected keyword from the dropdown.
    It fetches data for the selected keyword, specifically the universities with the most faculty members.
    Then, it prepares the data for the sunburst chart, including labels and values.
    Finally, it creates the sunburst chart and returns it with an appropriate title.

    Parameters:
    - keyword (str): The selected keyword from the dropdown.

    Returns:
    - fig (plotly.graph_objs.Figure): The sunburst chart displaying top universities by faculty members count
      for the selected keyword.
    """
    if keyword:
        # Fetch data for the selected keyword
        universities_data = fetch_universities_with_most_faculty(keyword)

        if universities_data:
            labels = [f"University: {row[0]}, Faculty Count: {row[1]}" for row in universities_data]
            values = [row[1] for row in universities_data]

            fig = go.Figure(go.Sunburst(
                labels=labels,
                parents=[''] * len(labels),  # All universities at the same level
                values=values,
            ))
            fig.update_layout(title=f"Top Universities by Faculty Members Count for '{keyword}'")
            return fig

    return go.Figure()

## Widget 4: Updates Pie Chart Based on Selected University Name by keyword relevant scores from neo4j
@app.callback(
    Output('keyword-scores-bar-chart', 'figure'),
    [Input('university-dropdown', 'value'),
     Input('ColorPicker', 'color')]
)
def update_keyword_scores_bar_chart(university_name, color):
    """
    Callback to update the bar chart based on the selected university name.

    This callback listens for changes in the selected university name from the dropdown.
    It fetches the keyword scores associated with the selected university.
    If data is available, it creates a bar chart displaying the keyword scores.
    If no data is available or no university name is selected, it returns an empty bar chart.

    Parameters:
    - university_name (str): The name of the selected university.
    - color (str): The selected color for the bars.

    Returns:
    - figure (plotly.graph_objs._figure.Figure): The bar chart figure to be displayed.
    """
    if university_name:
        keyword_scores_data = get_university_keyword_scores(university_name)

        if not keyword_scores_data.empty:
            # Create bar chart
            fig = go.Figure(data=[go.Bar(x=keyword_scores_data['keyword'], y=keyword_scores_data['total score'], marker_color=color)])
            fig.update_layout(title=f'Keyword Scores for {university_name}',
                              xaxis_title='Keyword Name', yaxis_title='Total Keyword Relevant Score (KRC)')
            return fig

    # If no data available or no university name selected, return an empty bar chart
    return go.Figure()

## Widget 5/6: Handling Addition and Deletion of User Research Interests (Backend Update)
@app.callback(
    Output('keyword-operation-feedback', 'children'),
    [Input('add-keyword-button', 'n_clicks'),
     Input('delete-keyword-button', 'n_clicks')],
    [State('add-research-interest-input', 'value'),
     State('delete-research-interest', 'value')]
)
def add_or_delete_keyword(add_clicks, delete_clicks, add_keyword, delete_keyword):
    """
    Callback to handle the addition or deletion of user research interests and provide feedback.

    This callback handles the addition or deletion of user research interests based on user interactions.
    It listens for clicks on the 'Add Keyword' and 'Delete Keyword' buttons and updates the database accordingly.
    It also provides feedback to the user about the success or failure of the operation.

    Parameters:
    - add_clicks (int): Number of clicks on the 'Add Keyword' button.
    - delete_clicks (int): Number of clicks on the 'Delete Keyword' button.
    - add_keyword (str): The keyword to be added.
    - delete_keyword (str): The keyword to be deleted.

    Returns:
    - feedback (dash.html.Div): Feedback message indicating the success or failure of the operation.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-keyword-button' and add_keyword:
            add_research_interest_with_procedure(add_keyword)
            return html.Div('Keyword added successfully', style={'color': 'green'})
        elif button_id == 'delete-keyword-button' and delete_keyword:
            delete_research_interest(delete_keyword)
            return html.Div('Keyword deleted successfully', style={'color': 'green'})
        else:
            return html.Div('Please enter a keyword', style={'color': 'red'})

## Widget 6: Handles Real-time Update of Delete Research Interests Dropdown
@app.callback(
    Output('delete-research-interest', 'options'),
    [Input('add-keyword-button', 'n_clicks'),
     Input('delete-keyword-button', 'n_clicks')]
)
def update_dropdown_options(add_clicks, delete_clicks):
    """
    Callback to update the options of the 'delete-research-interest' dropdown in real-time.

    This callback listens for clicks on the 'Add Keyword' and 'Delete Keyword' buttons to update
    the dropdown options dynamically. When a keyword is added or deleted, this function fetches
    all research interests from the database and constructs options for the dropdown accordingly.

    Parameters:
    - add_clicks (int): Number of clicks on the 'Add Keyword' button.
    - delete_clicks (int): Number of clicks on the 'Delete Keyword' button.

    Returns:
    - dropdown_options (list): Updated options for the 'delete-research-interest' dropdown.
    """
    ctx = dash.callback_context
    if ctx.triggered:
        # Fetch all research interests from the database
        research_interests = fetch_all_research_interests()

        # Construct options for the dropdown
        dropdown_options = [{'label': keyword, 'value': keyword} for keyword in research_interests]

        return dropdown_options
    else:
        # If no trigger, return the current options
        return dash.no_update

## Widget 5/6: Dynamic Updating of Research Interests Table
@app.callback(
    Output('research-interests-table', 'children'),
    [Input('add-keyword-button', 'n_clicks'),
     Input('delete-keyword-button', 'n_clicks')],
    [State('add-research-interest-input', 'value'),
     State('delete-research-interest', 'value')]
)
def update_keyword_table(add_clicks, delete_clicks, add_keyword, delete_keyword):
    """
    Callback to dynamically update the research interests table based on user interactions.

    This callback updates the table displaying research interests when a user adds or deletes a keyword.
    It listens for clicks on the 'Add Keyword' and 'Delete Keyword' buttons and updates the table accordingly.

    Parameters:
    - add_clicks (int): Number of clicks on the 'Add Keyword' button.
    - delete_clicks (int): Number of clicks on the 'Delete Keyword' button.
    - add_keyword (str): The keyword to be added.
    - delete_keyword (str): The keyword to be deleted.

    Returns:
    - button_group (dash_bootstrap_components.ButtonGroup): A button group containing buttons for each research interest.
    """
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-keyword-button' and add_keyword:
            add_research_interest_with_procedure(add_keyword)
        elif button_id == 'delete-keyword-button' and delete_keyword:
            delete_research_interest(delete_keyword)
    
    # Fetch all research interests from the database
    research_interests = fetch_all_research_interests()
    
    # Dynamically populate the table rows with keywords from the database
    button_group = dbc.ButtonGroup(
        [
            dbc.Button(
                keyword,
                color="secondary",
                href=f'/keyword/{i}',
                size="sm",  # Set button size to small
                style={'margin-right': '3px', 'margin-bottom': '3px'}  # Adjust margin
            ) 
            for i, keyword in enumerate(research_interests)
        ],
        size="sm",  # Set overall ButtonGroup size to small
        style={"flex-wrap": "wrap"}  # Allow buttons to wrap to next row when space runs out
    )

    return button_group

## Widget 7: Updates Recommended Faculty for User Research Interest Clicked by KRC Score
@app.callback(
    Output('professors-output', 'children'),
    [Input('url', 'pathname')]
)
def display_top_faculty(pathname):
    """
    Callback to update the display of top professors associated with the clicked keyword by KRC score.

    This callback listens for changes in the URL pathname, specifically when a keyword is clicked.
    It extracts the keyword index from the URL path, fetches the keyword associated with the index,
    and then fetches the top professors associated with that keyword. It constructs HTML to display
    the top professors along with their KRC scores. Additionally, it generates a pie chart showing
    the distribution of KRC scores among the top professors.

    Parameters:
    - pathname (str): The current URL pathname.

    Returns:
    - children (dash.html.Div or dash.dcc.Graph): The HTML or Graph component to be displayed.
    """
    if pathname is not None and pathname.startswith('/keyword/'):
        # Extract the keyword index from the URL path
        keyword_index = int(pathname.split('/')[-1])
        # Fetch the keyword associated with the index
        keyword = fetch_all_research_interests()[keyword_index]
        # Fetch top professors associated with the keyword
        professors = fetch_top_professors_for_keyword(keyword)
        # Create a pie chart with custom colors
        fig = go.Figure(data=[go.Pie(
            labels = [f"Name: {professor['professor']}, KRC: {professor['KRC']}" for professor in professors],
            values=[professor['KRC'] for professor in professors],
            marker=dict(colors=['#FFD700', '#48D1CC', '#FF8C00', '#90EE90', '#FFA07A', '#20B2AA', '#FFA500', '#32CD32', '#F0E68C', '#00CED1'])
        )])
        fig.update_layout(title=f"Recommended faculty by KRC scores associated with '{keyword}'")
        # Return the professors output along with the pie chart
        return dcc.Graph(figure=fig)
    else:
        # If no keyword is clicked, return empty output
        return html.Div()

## Widget 8: Updates Recommended Universities by User Research Interest Clicked by KRC Score
@app.callback(
    Output('universities-output', 'children'),
    [Input('url', 'pathname')]
)
def display_top_universities(pathname):
    """
    Callback to update the display of top universities associated with the clicked keyword.

    This callback listens for changes in the URL pathname, specifically when a keyword is clicked.
    It extracts the keyword index from the URL path, fetches the keyword associated with the index,
    and then fetches the top universities associated with that keyword. It then generates a pie chart
    displaying the recommended universities based on Knowledge Relevance and Contribution (KRC) scores.

    Parameters:
    - pathname (str): The current URL pathname.

    Returns:
    - children (dash.html.Div or dash.dcc.Graph): The HTML or Graph component to be displayed.
    """
    if pathname is not None and pathname.startswith('/keyword/'):
        # Extract the keyword index from the URL path
        keyword_index = int(pathname.split('/')[-1])
        # Fetch the keyword associated with the index
        keyword = fetch_all_research_interests()[keyword_index]
        # Fetch top universities associated with the keyword
        universities = fetch_top_universities_for_keyword(keyword)
        # Create data for the pie chart
        labels = [f"{university['university']}, KRC: {university['score']}" for university in universities]
        scores = [university['score'] for university in universities]
        
        # Define custom colors for the pie chart
        custom_colors = ['#1F77B4', '#2CA02C', '#D62728', '#9467BD', '#FF7F0E', '#A52A2A', '#800000', '#A52A2A', '#CD5C5C', '#800080']
        
        # Create the pie chart with custom colors
        fig = go.Figure(data=[go.Pie(labels=labels, values=scores, marker=dict(colors=custom_colors))])
        fig.update_layout(title=f"Recommended universities by KRC scores associated with '{keyword}'")
        
        # Return the pie chart
        return dcc.Graph(figure=fig)
    else:
        # If no keyword is clicked, return empty output
        return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)
