from imports import get_base64_image, process_latex, get_latex_code, show_graph, apply_operation, get_variables, add_operator, submit_expression
from imports import *
class symbook:
    def __init__(self):
        st.set_page_config(
            page_title="Symbook",
            page_icon = "icon_lowqual.png",
            layout="wide"
        )
        icon_base64 = get_base64_image("icon_lowqual.png")
        
        components.html(f'<img src="data:image/png;base64,{icon_base64}" alt="Icon" width="60" style="margin-top:6px">')       
        
    
        
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
            padding-top: 2.8rem;
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