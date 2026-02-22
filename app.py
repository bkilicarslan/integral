import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(
    page_title="Integral Master Pro",
    page_icon="∫",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- App Header ---
st.title("∫ Advanced Integral Visualizer")
st.markdown("""
This app calculates the **definite integral** of a function and visualizes the area under the curve.
It supports complex functions like $\sqrt{x^2 - 1}$ and $\exp(-x^2)$.
""")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Function Input")
func_str = st.sidebar.text_input("Enter f(x):", value="sqrt(x**2 - 1)")

st.sidebar.markdown("---")
st.sidebar.header("🔢 Integration Bounds")
col_a, col_b = st.sidebar.columns(2)
lower_bound = col_a.number_input("Lower (a)", value=1.0, step=0.1)
upper_bound = col_b.number_input("Upper (b)", value=5.0, step=0.1)

resolution = st.sidebar.select_slider(
    "Plot Smoothness",
    options=[100, 200, 500, 1000],
    value=500
)

# --- Math Logic ---
try:
    # 1. Parse the string into a SymPy expression
    # We replace ^ with ** automatically for user convenience
    x = sp.symbols('x')
    clean_expr = func_str.replace('^', '**')
    f_expr = sp.parse_expr(clean_expr, transformations='all')

    # 2. Calculate the Integral (Symbolic & Numerical)
    # Using .evalf() ensures we get a number even for complex results
    indefinite_integral = sp.integrate(f_expr, x)
    definite_integral_raw = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    
    # We take the Real part (sp.re) to handle cases where sqrt(neg) occurs
    numerical_value = float(sp.re(definite_integral_raw.evalf()))

    # 3. Create Numerical Function for Plotting
    # We use 'numpy' module for speed, but handle errors for undefined domains
    f_num = sp.lambdify(x, f_expr, modules=['numpy', 'cmath'])

    # --- UI Layout ---
    main_col, side_col = st.columns([2, 1])

    with side_col:
        st.subheader("📝 Mathematical Analysis")
        
        st.markdown("**Definite Integral:**")
        st.latex(rf"\int_{{{lower_bound}}}^{{{upper_bound}}} {sp.latex(f_expr)} \, dx")
        
        st.metric("Numerical Result", f"{numerical_value:.5f}")
        
        with st.expander("View Anti-derivative (Indefinite)"):
            st.latex(rf"{sp.latex(indefinite_integral)} + C")
        
        if "sqrt" in func_str and lower_bound < 1 and "x**2 - 1" in func_str:
            st.info("💡 **Domain Note:** For $\sqrt{x^2-1}$, the function is undefined for $|x| < 1$. The plot will show gaps where the values are non-real.")

    with main_col:
        # --- Plotting ---
        # Extend x range slightly for context
        padding = (upper_bound - lower_bound) * 0.2 if upper_bound != lower_bound else 1.0
        x_plot = np.linspace(lower_bound - padding, upper_bound + padding, resolution)
        
        # Calculate Y values safely
        y_plot = []
        for val in x_plot:
            try:
                res = f_num(val)
                # Filter out complex numbers for the visual plot
                if isinstance(res, complex):
                    y_plot.append(res.real if abs(res.imag) < 1e-6 else np.nan)
                else:
                    y_plot.append(float(res))
            except:
                y_plot.append(np.nan)

        # Area under the curve points
        x_fill = np.linspace(lower_bound, upper_bound, resolution)
        y_fill = []
        for val in x_fill:
            try:
                res = f_num(val)
                y_fill.append(res.real if isinstance(res, complex) else float(res))
            except:
                y_fill.append(0)

        fig = go.Figure()

        # Add shaded area
        fig.add_trace(go.Scatter(
            x=x_fill, y=y_fill,
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Area',
            hoverinfo='skip'
        ))

        # Add function line
        fig.add_trace(go.Scatter(
            x=x_plot, y=y_plot,
            mode='lines',
            name='f(x)',
            line=dict(color='#007BFF', width=3)
        ))

        fig.update_layout(
            title=f"Visualization of $f(x) = {sp.latex(f_expr)}$",
            xaxis_title="x",
            yaxis_title="f(x)",
            hovermode="x unified",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"🔍 **Parsing Error:** Could not interpret the function.")
    st.warning(f"Details: {e}")
    st.info("Try using standard Python notation: `sqrt(x**2 - 1)` or `exp(x)`")

st.markdown("---")
st.caption("Built with Streamlit, SymPy, and Plotly.")
