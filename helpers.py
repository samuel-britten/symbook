from imports import *
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

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
        except:
            return

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


def show_graph(exprs = None):
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
    
    if exprs is not None:
        js_functions = "[" + ",".join([f"'{expr}'" for expr in exprs]) + "]"
    else:
        js_functions = "[]"
    
    html_code = f"""
    <div style="background-color: {background_color}; padding-bottom: 2rem;">
        <canvas id="graphCanvas" width="1640" height="850" style="border:1px solid {text_color}; cursor: move; top:10px;  position: relative;
            "></canvas>
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
    components.html(html_code, height=950, width = 1640)