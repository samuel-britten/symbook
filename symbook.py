import streamlit as st
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from sympy import *
from spb import *
import streamlit as st
from streamlit.components.v1 import html
import os
import streamlit.components.v1 as components
#init_session()

def process_latex(expr):
    """Convert LaTeX expressions to JavaScript math"""
    # Handle expressions with curly braces in exponents
    while '{' in expr and '}' in expr:
        start = expr.find('^{')
        if start != -1:
            # Find matching closing brace
            count = 1
            end = start + 2
            while count > 0 and end < len(expr):
                if expr[end] == '{':
                    count += 1
                elif expr[end] == '}':
                    count -= 1
                end += 1
            
            if count == 0:
                # Replace ^{...} with ^(...)
                power = expr[start+2:end-1]
                expr = expr[:start] + '^(' + power + ')' + expr[end:]
        else:
            break
    
    return expr

st.set_page_config(
    page_title="Symbook",
    layout="wide"
)

def add_operator(operator):
    cursor_pos = st.session_state.get('cursor_pos', len(st.session_state['temp_expr']))
    current_expr = st.session_state['temp_expr']
    if operator == '=':
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '=' + current_expr[cursor_pos:]
    elif operator == "a":
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '\sum_{}^{}' + current_expr[cursor_pos:]
    elif operator == "b":
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '\prod_{}^{}' + current_expr[cursor_pos:]
    elif operator == "c":
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '\int' + current_expr[cursor_pos:]
    elif operator == "d":
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '\int_{}^{}' + current_expr[cursor_pos:]
    elif operator == "e":
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '\lim_{ \\to }' + current_expr[cursor_pos:]
    else:
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + operator + current_expr[cursor_pos:]

def submit_expression():
    key = st.session_state['current_expr']
    new_expr = st.session_state['temp_expr']
    if new_expr.strip():
        try:
            transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
            if '=' in new_expr:
                left, right = new_expr.split('=')
                left_expr = parse_expr(left, transformations=transformations)
                right_expr = parse_expr(right, transformations=transformations)
                Eq(left_expr, right_expr)
            else:
                parse_expr(new_expr, transformations=transformations)
            st.session_state['expressions'][key] = new_expr
            st.session_state['edit_states'][key] = False
            st.session_state['temp_expr'] = ''
        except Exception as e:
            st.error("Invalid expression")

def get_variables(expr):
    transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
    if '=' in expr:
        left, right = expr.split('=')
        left_expr = parse_expr(left, transformations=transformations)
        right_expr = parse_expr(right, transformations=transformations)
        sym_expr = Eq(left_expr, right_expr)
    else:
        sym_expr = parse_expr(expr, transformations=transformations)
    return sorted([str(s) for s in sym_expr.free_symbols])

def get_latex_code(expr, result=None):
    transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
    if '=' in expr:
        left, right = expr.split('=')
        left_expr = parse_expr(left, transformations=transformations)
        right_expr = parse_expr(right, transformations=transformations)
        sym_expr = Eq(left_expr, right_expr)
    else:
        sym_expr = parse_expr(expr, transformations=transformations)
    
    latex_code = f"${latex(sym_expr)}$"
    if result:
        latex_code += f"\n\nResult:\n${latex(result)}$"
    return latex_code

def apply_operation(expr, operation, var=None, val=None):
    transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
    if '=' in expr:
        left, right = expr.split('=')
        left_expr = parse_expr(left, transformations=transformations)
        right_expr = parse_expr(right, transformations=transformations)
        sym_expr = Eq(left_expr, right_expr)
    else:
        sym_expr = parse_expr(expr, transformations=transformations)
    
    if operation == "Simplify":
        return simplify(sym_expr)
    elif operation == "Solve":
        if isinstance(sym_expr, Eq):
            return solve(sym_expr)
        return solve(sym_expr)
    elif operation == "Find roots":
        return solve(sym_expr, dict=True)
    elif operation == "Evaluate":
        return N(sym_expr)
    elif operation == "Substitute":
        if var and val:
            try:
                val_expr = parse_expr(val, transformations=transformations)
                return sym_expr.subs(Symbol(var), val_expr)
            except:
                return "Invalid substitution"
    return sym_expr

def show_graph(exprs):
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
    
    html_code = f"""
    <div style="background-color: {background_color}; padding-bottom: 2rem;">
        <canvas id="graphCanvas" width="800" height="800" style="border:1px solid {text_color}; cursor: move;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('graphCanvas');
        const ctx = canvas.getContext('2d');
        
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        const width = canvas.width;
        const height = canvas.height;
        let scale = 40;
        const minScale = 10;
        const maxScale = 200;
        
        let offsetX = 0;
        let offsetY = 0;
        let isDragging = false;
        let startX, startY;

        const functions = {js_functions};
        
        function drawGrid() {{
            ctx.strokeStyle = '{secondary_background_color}';
            ctx.lineWidth = 1;
            
            const xLines = Math.ceil(width / scale);
            const yLines = Math.ceil(height / scale);
            
            for(let x = -xLines; x <= xLines; x++) {{
                const xPos = x * scale + offsetX % scale;
                ctx.beginPath();
                ctx.moveTo(xPos, -height/2);
                ctx.lineTo(xPos, height/2);
                ctx.stroke();
                
                ctx.save();
                ctx.scale(1, -1);
                ctx.fillStyle = '{text_color}';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                if (Math.abs(x) > 0.1) {{
                    const label = (x * scale / 40).toFixed(2).replace(/\.00$/, '');
                    ctx.fillText(label, xPos, 5);
                }}
                ctx.restore();
            }}
            
            for(let y = -yLines; y <= yLines; y++) {{
                const yPos = y * scale + offsetY % scale;
                ctx.beginPath();
                ctx.moveTo(-width/2, yPos);
                ctx.lineTo(width/2, yPos);
                ctx.stroke();
                
                ctx.save();
                ctx.scale(1, -1);
                ctx.fillStyle = '{text_color}';
                ctx.font = '10px Arial';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'middle';
                if (Math.abs(y) > 0.1) {{
                    const label = (y * scale / 40).toFixed(2).replace(/\.00$/, '');
                    ctx.fillText(label, -5, -yPos);
                }}
                ctx.restore();
            }}
        }}
        
        function drawAxes() {{
            ctx.strokeStyle = '{text_color}';
            ctx.lineWidth = 2;
            
            ctx.beginPath();
            ctx.moveTo(-width/2, 0);
            ctx.lineTo(width/2, 0);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(0, -height/2);
            ctx.lineTo(0, height/2);
            ctx.stroke();
        }}
        
        function plotFunction() {{
            let colors = ['{primary_color}', '#FF8C00', '#9370DB', '#20B2AA', '#CD5C5C'];
            functions.forEach((func, index) => {{
                ctx.strokeStyle = colors[index % colors.length];
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                const xStart = (-width/2 - offsetX) / scale;
                const xEnd = (width/2 - offsetX) / scale;
                const step = (xEnd - xStart) / 1000;
                
                let isFirst = true;
                
                for(let x = xStart; x <= xEnd; x += step) {{
                    try {{
                        let expression = func
                        
                        
                        const y = eval(expression);
                        
                        if (isNaN(y) || !isFinite(y)) continue;
                        
                        const px = x * scale;
                        const py = y * scale;
                        
                        if (Math.abs(py) > height * 2) continue;
                        
                        if (isFirst) {{
                            ctx.moveTo(px, py);
                            isFirst = false;
                        }} else {{
                            ctx.lineTo(px, py);
                        }}
                    }} catch (e) {{
                        continue;
                    }}
                }}
                ctx.stroke();
            }});
        }}
        
        function redraw() {{
            ctx.save();
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.clearRect(0, 0, width, height);
            ctx.restore();
            
            ctx.save();
            ctx.translate(width/2 + offsetX, height/2 + offsetY);
            ctx.scale(1, -1);
            
            drawGrid();
            drawAxes();
            plotFunction();
            
            ctx.restore();
        }}

        canvas.addEventListener('mousedown', function(e) {{
            isDragging = true;
            const rect = canvas.getBoundingClientRect();
            startX = e.clientX - offsetX;
            startY = e.clientY - offsetY;
            canvas.style.cursor = 'grabbing';
        }});

        canvas.addEventListener('mousemove', function(e) {{
            if (isDragging) {{
                offsetX = e.clientX - startX;
                offsetY = e.clientY - startY;
                redraw();
            }}
        }});

        canvas.addEventListener('mouseup', function() {{
            isDragging = false;
            canvas.style.cursor = 'move';
        }});

        canvas.addEventListener('mouseleave', function() {{
            isDragging = false;
            canvas.style.cursor = 'move';
        }});

        canvas.addEventListener('wheel', function(event) {{
            event.preventDefault();
            
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left - width/2 - offsetX;
            const mouseY = -(event.clientY - rect.top - height/2) + offsetY;
            
            const zoomIntensity = 0.1;
            const wheel = event.deltaY < 0 ? 1 : -1;
            const zoom = Math.exp(wheel * zoomIntensity);
            
            const newScale = scale * zoom;
            
            if (newScale >= minScale && newScale <= maxScale) {{
                scale = newScale;
                redraw();
            }}
        }}, {{ passive: false }});

        window.addEventListener('resize', function() {{
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            redraw();
        }});
        
        redraw();
    </script>
    """
    components.html(html_code, height=800)

class symbook:
    def __init__(self):
        title = st.title("Symbook")
    
        
        def get_js_expr(expr):
            function_input = expr
            
            
            function_input = (function_input.replace("y=", "").strip())
            function_input = process_latex(function_input)
            
            
            
            function_input = (function_input
                            .replace("\left(", "")
                            .replace("\\right)", "")
                            .replace("{", "(")
                            .replace("}", ")")
                            .replace("\\", "")
                            .replace(" ", "")
                            .replace("sin", "Math.sin")
                            .replace("cos", "Math.cos")
                            .replace("tan", "Math.tan")
                            .replace("sqrt", "Math.sqrt")
                            .replace("log", "Math.log")
                            .replace("e", "Math.E")
                            .replace("pi", "Math.PI")
                            .replace("^", "**"))
            return function_input
        
        
        
        #components.html(html_code, height=450)
        
        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
     

        self.expr_count = 0
        
        latex_code = None
        st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 20rem; /* Significantly increase bottom padding */
            padding-left: 2rem;
            padding-right: 0rem; /* Increase right padding */
            max-height: none; /* Remove max height restriction */
            overflow-y: auto; /* Enable vertical scrolling */
        }

        div[data-testid="stCodeBlock"] {
            max-width: none !important;
            width: 100% !important;
            white-space: pre-wrap !important;
            overflow-x: visible !important;
        }

        [data-testid="column"] [data-testid="stVerticalBlock"] {
            gap: 0rem;
        }
    </style>
""", unsafe_allow_html=True)
        
        if 'expressions' not in st.session_state:
            st.session_state['expressions'] = {'0': ''}
        if 'edit_states' not in st.session_state:
            st.session_state['edit_states'] = {'0': True}
        if 'current_expr' not in st.session_state:
            st.session_state['current_expr'] = '0'
        if 'keyboard_visible' not in st.session_state:
            st.session_state['keyboard_visible'] = False
        if 'temp_expr' not in st.session_state:
            st.session_state['temp_expr'] = ''
            
        expr_column = st.columns([0.7, 0.3], gap='small')

        with expr_column[0]:
            num_expressions = len(st.session_state['expressions'])
            total_width = 0.2 * num_expressions
            remaining_width = 1 - total_width
            col_widths = [0.2] * num_expressions + [remaining_width] if remaining_width > 0 else [1/num_expressions] * num_expressions
            cols = st.columns(col_widths)
            
            for idx, (key, expr) in enumerate(st.session_state['expressions'].items()):
                with cols[idx]:
                    if expr.strip():
                        try:
                            transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
                            if '=' in expr:
                                left, right = expr.split('=')
                                left_expr = parse_expr(left, transformations=transformations)
                                right_expr = parse_expr(right, transformations=transformations)
                                sym_expr = Eq(left_expr, right_expr)
                            else:
                                sym_expr = parse_expr(expr, transformations=transformations)
                            button_label = f'${latex(sym_expr)}$'
                        except:
                            button_label = f'Expr {int(key) + 1}'
                    else:
                        button_label = f'Expr {int(key) + 1}'
                    
                    if st.button(
                        button_label,
                        key=f'nav_{key}',
                        type='primary' if key == st.session_state['current_expr'] else 'secondary'
                    ):
                        st.session_state['current_expr'] = key
                        st.rerun()

            st.divider()

            key = st.session_state['current_expr']
            if st.session_state['edit_states'][key]:
                input_col, kb_col, submit_col = st.columns([0.8, 0.1, 0.1])
                
                if st.session_state['temp_expr'] == '':
                    st.session_state['temp_expr'] = st.session_state['expressions'][key]
                
                with input_col:
                    new_expr = st.text_input(
                        'Enter expression:',
                        value=st.session_state['temp_expr'],
                        key=f'input_{key}',
                        label_visibility="collapsed"
                    )
                    st.session_state['temp_expr'] = new_expr
                    
                with kb_col:
                    if st.button('⌨️', key='keyboard_toggle'):
                        st.session_state['keyboard_visible'] = not st.session_state['keyboard_visible']
                        st.rerun()
                
                with submit_col:
                    if st.button('✓', key='submit'):
                        submit_expression()
                        st.rerun()
                
                if st.session_state['keyboard_visible']:
                    
                        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 1, .93, .9, .9, .9, .9, .9, .9, .9, 15])[:-1]
                        with col1:
                            if st.button('$＋$', key='add', on_click=add_operator, args=('+')):
                                st.rerun()
                        with col2:
                            if st.button('$－$', key='subtract', on_click=add_operator, args=('-')):
                                st.rerun()
                        with col3:
                            if st.button('$\\times$', key='multiply', on_click=add_operator, args=('*')):
                                st.rerun()
                        with col4:
                            if st.button('$\div$', key='divide', on_click=add_operator, args=('/')):
                                st.rerun()
                        with col5:
                            if st.button('$＝$', key='equals', on_click=add_operator, args=('=')):
                                st.rerun()
                        with col6:
                            if st.button('$\sum$', key='sum', on_click=add_operator, args=('a')):
                                st.rerun()
                        with col7:
                            if st.button('$\prod$', key='product', on_click=add_operator, args=('b')):
                                st.rerun()
                        with col8:
                            if st.button('$\int$', key='integral', on_click=add_operator, args=('c')):
                                st.rerun()
                        with col9:
                            if st.button('$\int_a^b$', key='definite_integral', on_click=add_operator, args=('d')):
                                st.rerun()
                        with col10:
                            if st.button('$\\lim_{\\to}$', key='limit', on_click=add_operator, args=('e')):
                                st.rerun()
            else:
                try:
                    transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
                    if '=' in st.session_state['expressions'][key]:
                        left, right = st.session_state['expressions'][key].split('=')
                        left_expr = parse_expr(left, transformations=transformations)
                        right_expr = parse_expr(right, transformations=transformations)
                        sym_expr = Eq(left_expr, right_expr)
                    else:
                        sym_expr = parse_expr(st.session_state['expressions'][key], transformations=transformations)
                    col1, col2, col3, col4, col5, col6 = st.columns([0.3, 0.3, 0.1, 0.1, 0.1, 0.2])
                    
                    with col1:
                        st.latex(latex(sym_expr))
                    with col2:
                        operation = st.selectbox(
                            'Operation',
                            ['Select operation', 'Simplify', 'Solve', 'Find roots', 'Evaluate', 'Substitute'],
                            key=f'operation_{key}',
                            label_visibility="collapsed"
                        )
                        if operation == 'Substitute':
                            variables = get_variables(st.session_state['expressions'][key])
                            if variables:
                                var = st.selectbox('Variable', variables, key=f'var_{key}')
                                val = st.text_input('Value', key=f'val_{key}')
                                if val:
                                    result = apply_operation(st.session_state['expressions'][key], operation, var, val)
                                    st.latex(latex(result))
                                    st.session_state[f'result_{key}'] = result
                        elif operation != 'Select operation':
                            result = apply_operation(st.session_state['expressions'][key], operation)
                            st.latex(latex(result))
                            st.session_state[f'result_{key}'] = result
                    with col3:
                        if st.button('✒', key=f'edit_button_{key}'):
                            st.session_state['edit_states'][key] = True
                            st.session_state['temp_expr'] = st.session_state['expressions'][key]
                            st.rerun()
                    with col4:
                        if num_expressions > 1 and st.button('🗑', key=f'delete_{key}'):
                            del st.session_state['expressions'][key]
                            del st.session_state['edit_states'][key]
                            new_expressions = {}
                            new_edit_states = {}
                            for i, (k, v) in enumerate(st.session_state['expressions'].items()):
                                new_expressions[str(i)] = v
                                new_edit_states[str(i)] = st.session_state['edit_states'][k]
                            st.session_state['expressions'] = new_expressions
                            st.session_state['edit_states'] = new_edit_states
                            if key == st.session_state['current_expr']:
                                st.session_state['current_expr'] = '0'
                            elif int(st.session_state['current_expr']) > int(key):
                                st.session_state['current_expr'] = str(int(st.session_state['current_expr']) - 1)
                            st.rerun()
                    with col5:
                        if st.button(f'$\\LaTeX$', key=f'latex_{key}'):
                            latex_code = get_latex_code(st.session_state['expressions'][key], 
                                                      st.session_state.get(f'result_{key}', None))
                    with col6:
                        if st.button('Plot', key=f'plot_{key}'):
                            expr = get_js_expr(get_latex_code(st.session_state['expressions'][key], 
                                             st.session_state.get(f'result_{key}', None))[1:-1])
                            if 'plot_exprs' not in st.session_state:
                                st.session_state['plot_exprs'] = []
                            if expr not in st.session_state['plot_exprs']:
                                st.session_state['plot_exprs'].append(expr)
                            st.rerun()

                    if latex_code is not None:
                        st.code(latex_code, language='latex')
                        
                except Exception as e:
                    st.write("Invalid expression")
                    st.session_state['edit_states'][key] = True
                    st.rerun()

            if 'plot_exprs' in st.session_state and st.session_state['plot_exprs']:
                st.divider()
                show_graph(st.session_state['plot_exprs'])

        with expr_column[1]:
            if st.button('➕ Add Expression'):
                new_idx = str(len(st.session_state['expressions']))
                st.session_state['expressions'][new_idx] = ''
                st.session_state['edit_states'][new_idx] = True
                st.session_state['current_expr'] = new_idx
                st.session_state['temp_expr'] = ''
                st.rerun()
        
        
        
symbook()