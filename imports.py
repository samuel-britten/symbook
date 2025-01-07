import streamlit as st
import base64
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from sympy import *
from spb import *
import streamlit as st
from streamlit.components.v1 import html
import os
import streamlit.components.v1 as components
from helpers import *

def plot_exprs(exprs):
    try:
        primary_color = st.get_option("theme.primaryColor")
        background_color = st.get_option("theme.backgroundColor")
        secondary_background_color = st.get_option("theme.secondaryBackgroundColor")
        text_color = st.get_option("theme.textColor")
    except:
        primary_color = "#FF4B4B"
        background_color = "#FFFFFF"
        secondary_background_color = "#F0F2F6"
        text_color = "#262730"
    
    js_functions = "[" + ",".join([f"'{expr}'" for expr in exprs]) + "]"
    
    # Add wrapper div and ensure JavaScript runs in iframe
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <div style="background-color: {background_color}; padding-bottom: 2rem;">
            <canvas id="graphCanvas" width="800" height="800" style="border:1px solid {text_color}; cursor: move;"></canvas>
        </div>

        <script>
            // ...rest of your JavaScript code...
        </script>
    </body>
    </html>
    """
    
    # Use components.html with iframe configuration
    components.html(
        html_code,
        height=800,
        scrolling=False,
        element_style={"width": "100%"},
        sandbox=["allow-scripts"]
    )

# ...rest of your code...
