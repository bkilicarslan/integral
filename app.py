import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF

# --- Page Config ---
st.set_page_config(page_title="Integral Master Pro", page_icon="∫", layout="wide")

# --- PDF Generation Function ---
def create_pdf(func_str, lower, upper, indefinite, f_b, f_a, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Modern fpdf2 syntax for line breaks
    pdf.cell(0, 10, txt="Integral Calculation Report", new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="", new_x="LMARGIN", new_y="NEXT") # Blank line
    pdf.cell(0, 10, txt=f"Function: f(x) = {func_str}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=f"Bounds: From {lower} to {upper}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(0, 10, txt="", new_x="LMARGIN", new_y="NEXT") # Blank line
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt="Step-by-Step Solution:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Arial", size=12)
    
    # FIX: Add spaces around operators so FPDF can word-wrap long math strings!
    indef_str = str(indefinite).replace('**', '^').replace('+', ' + ').replace('-', ' - ').replace('*', ' * ')
    
    pdf.multi_cell(0, 10, txt=f"1. Find the anti-derivative F(x):\n    F(x) = {indef_str}")
    pdf.multi_cell(0, 10, txt="2. Apply Fundamental Theorem of Calculus: F(b) - F(a)")
    
    fb_val = float(sp.re(f_b))
    fa_val = float(sp.re(f_a))
    
    pdf.multi_cell(0, 10, txt=f"    F({upper}) = {fb_val:.4f}")
    pdf.multi_cell(0, 10, txt=f"    F({lower}) = {fa_val:.4f}")
    pdf.multi_cell(0, 10, txt=f"3. Final Result: {fb_val:.4f} - ({fa_val:.4f}) = {result:.5f}")
    
    return bytes(pdf.output())

# --- Main App ---
st.title("∫ Integral Master with Graph & PDF")

# Sidebar
st.sidebar.header("📥 Input Parameters")
func_str = st.sidebar.text_input("Enter f(x):", value="sqrt(x**2 - 1)")
lower_bound = st.sidebar.number_input("Lower Bound (a)", value=1.0, step=0.5)
upper_bound = st.sidebar.number_input("Upper Bound (b)", value=5.0, step=0.5)

# --- Logic & Processing ---
try:
    # 1. Parse Math
    x = sp.symbols('x')
    clean_expr = func_str.replace('^', '**')
    f_expr = sp.parse_expr(clean_expr, transformations='all')

    # 2. Calculus Steps
    indefinite_integral = sp.integrate(f_expr, x)
    definite_integral_raw = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    numerical_value = float(sp.re(definite_integral_raw.evalf()))

    # 3. Step values for PDF and UI
    f_b = indefinite_integral.subs(x, upper_bound).evalf()
    f_a = indefinite_integral.subs(x, lower_bound).evalf()

    # --- UI Layout ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("📝 Step-by-Step")
        st.latex(rf"F(x) = \int {sp.latex(f_expr)} dx")
        st.latex(rf"= {sp.latex(indefinite_integral)}")
        
        st.write("**Evaluate at bounds:**")
        st.latex(rf"F({upper_bound}) = {float(sp.re(f_b)):.4f}")
        st.latex(rf"F({lower_bound}) = {float(sp.re(f_a)):.4f}")
        st.success(f"**Final Result:** {numerical_value:.5f}")

        # PDF Download - Wrapped in its own try/except so it doesn't crash the graph if it fails
        try:
            pdf_data = create_pdf(func_str, lower_bound, upper_bound, indefinite_integral, f_b, f_a, numerical_value)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name="integral_report.pdf",
                mime="application/pdf",
            )
        except Exception as pdf_error:
            st.error(f"PDF Generation Failed: {pdf_error}")

    with col1:
        st.subheader("📊 Function Graph")
        x_plot = np.linspace(lower_bound - 1, upper_bound + 1, 500)
        f_num = sp.lambdify(x, f_expr, modules=['numpy', 'cmath'])
        
        y_plot = []
        for val in x_plot:
            try:
                res = f_num(val)
                if isinstance(res, complex):
                    y_plot.append(res.real if abs(res.imag) < 1e-6 else np.nan)
                else:
                    y_plot.append(float(res))
            except:
                y_plot.append(np.nan)

        x_fill = np.linspace(lower_bound, upper_bound, 300)
        y_fill = []
        for val in x_fill:
            try:
                res = f_num(val)
                y_fill.append(res.real if isinstance(res, complex) and abs(res.imag) < 1e-6 else float(res))
            except:
                y_fill.append(0)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_fill, y=y_fill,
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.3)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Area',
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=x_plot, y=y_plot, 
            mode='lines', 
            name='f(x)', 
            line=dict(color='#007BFF', width=3)
        ))

        fig.update_layout(
            title=f"Area under {func_str} from {lower_bound} to {upper_bound}",
            xaxis_title="x",
            yaxis_title="f(x)",
            template="plotly_white",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Computation Error: {e}")
    st.info("Ensure you are using standard math notation (e.g., `x**2` or `sin(x)`).")
