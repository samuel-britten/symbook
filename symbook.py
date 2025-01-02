import streamlit as st
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from PyDesmos import *
from sympy import *
from bokeh.plotting import *
from spb import *

st.set_page_config(
    page_title="Symbook",
    layout="wide"
)

def add_operator(operator):
    cursor_pos = st.session_state.get('cursor_pos', len(st.session_state['temp_expr']))
    current_expr = st.session_state['temp_expr']
    if operator == '=':
        st.session_state['temp_expr'] = current_expr[:cursor_pos] + '=' + current_expr[cursor_pos:]
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

class symbook:
    def __init__(self):
        new = 2 # open in a new tab, if possible
        url = "http://docs.python.org/library/webbrowser.html"
        webbrowser.open(url,new=new)

        st.title("Symbook")
        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
        self.G = Graph('my graph')

        self.expr_count = 0

        self.G.html = self.G.html.replace("src=\"https://www.desmos.com/api/v1.7/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6\"></script>", "src=\"https://www.desmos.com/api/v1.11/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6\"></script>") #+ r"\ncalculator.updateSettings({allowComplex: true})"
        self.G.html += "calculator.updateSettings({allowComplex: true, invertedColors: true});\n"
        self.G.html += "var state = calculator.getState();\n"
        self.G.html += "calculator.graphSettings.complex = true;\n"
        self.G.html += "calculator.graphSettings.restrictedFunctions = true;\n"
        self.G.html += "calculator.settings.complex = true;\n"
        self.G.html += "console.log(calculator);"
        
        latex_code = None
        st.markdown("""
    <style>
        .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 0rem;
        
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
                    keyboard_container = st.container()
                    with keyboard_container:
                        st.write("")
                        col1, col2, col3, col4, col5, col6 = st.columns([0.1, 0.1, 0.1, 0.1, 0.1, 0.5])
                        with col1:
                            if st.button('＋', key='add', on_click=add_operator, args=('+')):
                                st.rerun()
                        with col2:
                            if st.button('－', key='subtract', on_click=add_operator, args=('-')):
                                st.rerun()
                        with col3:
                            if st.button('×', key='multiply', on_click=add_operator, args=('*')):
                                st.rerun()
                        with col4:
                            if st.button('÷', key='divide', on_click=add_operator, args=('/')):
                                st.rerun()
                        with col5:
                            if st.button('＝', key='equals', on_click=add_operator, args=('=')):
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
                            #x=symbols('x')
                            #figure = plot(x, show=True)
                            #st.bokeh_chart(figure, use_container_width=False)
                            #p = figure(title="simple line example", x_axis_label="x", y_axis_label="y")
                            #p.line(x, y, legend_label="Trend", line_width=2)
                            #show(p)
                            #st.bokeh_chart(p, use_container_width=True)
                            
                            
                            with self.G:
                                text = st.session_state['expressions'][key]

                                self.G.html += "calculator.setExpression({ id: 'x', latex:" + f"'{text}'" + " });"
                               
                    if latex_code is not None:
                        st.code(latex_code, language='latex')
                        
                except Exception as e:
                    st.write("Invalid expression")
                    st.session_state['edit_states'][key] = True
                    st.rerun()

        with expr_column[1]:
            if st.button('➕ Add Expression'):
                new_idx = str(len(st.session_state['expressions']))
                st.session_state['expressions'][new_idx] = ''
                st.session_state['edit_states'][new_idx] = True
                st.session_state['current_expr'] = new_idx
                st.session_state['temp_expr'] = ''
                st.rerun()
symbook()