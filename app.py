import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- Page Config ---
st.set_page_config(page_title="Integral Master Pro", page_icon="∫", layout="wide")

# --- PDF Generation Function ---
def create_pdf(func_str, lower, upper, indefinite, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Integral Calculation Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Function: f(x) = {func_str}", ln=True)
    pdf.cell(200, 10, txt=f"Bounds: From {lower} to {upper}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Step-by-Step Solution:", ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"1. Find the anti-derivative F(x):\n   F(x) = {indefinite}")
    
    # Calculate step values
    x_sym = sp.symbols('x')
    f_b = indefinite.subs(x_sym, upper).evalf()
    f_a = indefinite.subs(x_sym, lower).evalf()
    
    pdf.multi_cell(0, 10, txt=f"2. Apply Fundamental Theorem of Calculus: F(b) - F(a)")
    pdf.multi_cell(0, 10, txt=f"   F({upper}) = {f_b}")
    pdf.multi_cell(0, 10, txt=f"   F({lower}) = {f_a}")
    pdf.multi_cell(0, 10, txt=f"3. Final Result: {f_b} - ({f_a}) = {result:.5f}")
    
    return pdf.output(dest='S')

# --- Main App ---
st.title("∫ Integral Master with PDF Export")

# Sidebar
st.sidebar.header("📥 Input")
func_str = st.sidebar.text_input("Enter f(x):", value="sqrt(x**2 - 1)")
lower_bound = st.sidebar.number_input("Lower (a)", value=1.0)
upper_bound = st.sidebar.number_input("Upper (b)", value=5.0)

try:
    x = sp.symbols('x')
    clean_expr = func_str.replace('^', '**')
    f_expr = sp.parse_expr(clean_expr, transformations='all')

    # Calculus Logic
    indefinite_integral = sp.integrate(f_expr, x)
    definite_integral_raw = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    numerical_value = float(sp.re(definite_integral_raw.evalf()))

    # Steps for UI
    f_b = indefinite_integral.subs(x, upper_bound).evalf()
    f_a = indefinite_integral.subs(x, lower_bound).evalf()

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("📝 Step-by-Step")
        st.latex(rf"F(x) = \int {sp.latex(f_expr)} dx = {sp.latex(indefinite_integral)}")
        st.write("**Evaluate at bounds:**")
        st.latex(rf"F({upper_bound}) = {f_b:.4f}")
        st.latex(rf"F({lower_bound}) = {f_a:.4f}")
        st.success(f"Result: {numerical_value:.5f}")

        # PDF Download Button
        pdf_data = create_pdf(func_str, lower_bound, upper_bound, indefinite_integral, numerical_value)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name="integral_calculation.pdf",
            mime="application/pdf",
        )

    with col1:
        # Plotting
        x_plot = np.linspace(lower_bound - 1, upper_bound + 1, 500)
        f_num = sp.lambdify(x, f_expr, modules=['numpy', 'cmath'])
        
        y_plot = []
        for val in x_plot:
            try:
                res = f_num(val)
                y_plot.append(float(res.real) if hasattr(res, 'real') else float(res))
            except: y_plot.append(np.nan)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_plot, y=y_plot, mode='lines', name='f(x)', line=dict(color='#007BFF')))
        fig.update_layout(title="Function Visualization", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error parsing function. Make sure to use 'x' as the variable.")
