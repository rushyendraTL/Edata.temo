# --- File: app.py ---

import os
import flask
from dotenv import load_dotenv

import dash
from dash import dcc, html, Input, Output

# --- Project Setup ---
# 1. Create a directory for your project (e.g., dash_flask_login_pages_app).
# 2. Inside that directory, create this file (app.py).
# 3. Create a subdirectory named 'pages'.
# 4. Create the page files (home.py, protected_page.py, login.py) inside 'pages/'.
# 5. Create a file named '.env' in the main project directory.
# 6. Create a file named 'requirements.txt' in the main project directory.

# --- Configuration and Initialization ---
load_dotenv()  # Load variables from .env file
server = flask.Flask(__name__)
server.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

server.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# --- Dash App Initialization (using Pages) ---
# Pass the Flask server instance, enable pages, and set pages folder.
# 'routes_pathname_prefix' sets the base URL for all Dash pages registered
# via the 'pages' plugin. This helps avoid conflicts with Flask routes like '/login'.
GOOGLE_FONT_URL = 'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap'
GOOGLE_ICON_URL = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0'
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,  # Often needed with dynamic layouts/auth
    pages_folder='pages',
    # All Dash pages will be under /app/ (e.g., /app/, /app/protected)
    routes_pathname_prefix='/app/',
    requests_pathname_prefix='/app/',
    external_stylesheets=[
        GOOGLE_FONT_URL,
        GOOGLE_ICON_URL,
    ],
    # external_scripts=[
    #     'https://cdn.plot.ly/plotly-latest.min.js'
    # ]
)
app.title = "Dash App"
app.scripts.config.serve_locally = True  # Serve local assets like images
app.css.config.serve_locally = True  # Serve local CSS files

# --- Main Dash Layout (App Shell) ---
# This defines the overall structure that wraps around the content from the 'pages/' directory.
app.layout = html.Div([
    dcc.Store(id='filter-store', storage_type='session', data={
        'timespan': None,
        'start_date': None,
        'end_date': None,
        'make': None,
        'model': None,
        'top_n': 10,
        'country': None,
        'is_ev': None,
        'year_range': [1995, 2025],
        'pro': False,
        'pro_mode': 'benchmark',
        'target_company': None

    }),

    # Wrapper Div for main content area to enable flex-grow
    html.Div(id='site-content', children=[
        # dash.page_container is the placeholder where the layout defined in
        # the currently active page file (from the 'pages/' folder) will be rendered.
        dash.page_container
        # Allow content scrolling if needed
    ],
        style={'overflowY': 'clip', 'flexGrow': 1, 'minHeight': '0'}
    ),

    # Simple Footer
    # html.Footer("This is the footer.", style={
    #     'padding': '1rem',
    #     'backgroundColor': '#f0f0f0',
    #     'textAlign': 'center',
    #     'marginTop': 'auto'  # Pushes footer to bottom in flex container
    # }),

    # dcc.Location is needed for callbacks that depend on the URL pathname.
    dcc.Location(id='url', refresh=False)
    # Use minHeight to be flexible
], style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'})



# --- Run the Application ---
if __name__ == '__main__':
    print("Starting Flask server for Dash app...")
    print(f"Access the app at http://127.0.0.1:8083/app/")
    # Use the Flask server's run method with debug=True for hot reloading
    server.run(debug=False, port=8083, host='0.0.0.0',threaded=True,use_reloader=False)
