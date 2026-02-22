import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Integral Master", page_icon="∫", layout="wide")

st.title("∫ Integral Calculator & Visualizer")
st.markdown("Enter a function of **x** to calculate the definite integral and visualize the area under the curve.")

# --- Sidebar Inputs ---
st.sidebar.header("Function Parameters")
func_input = st.sidebar.text_input("Enter function f(x):", value="sin(x) + 0.5*x")
lower_bound = st.sidebar.number_input("Lower bound (a):", value=0.0)
upper_bound = st.sidebar.number_input("Upper bound (b):", value=10.0)
resolution = st.sidebar.slider("Graph Resolution", 50, 1000, 500)

try:
    # --- Logic: Symbolics with SymPy ---
    x = sp.symbols('x')
    f_expr = sp.parse_expr(func_input.replace('^', '**')) # Handle common user typo
    
    # Calculate Definite Integral
    integral_val = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    
    # Create Numerical Function for Plotting
    f_num = sp.lambdify(x, f_expr, "numpy")
    
    # --- Layout: Results ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Result")
        st.latex(rf"\int_{{{lower_bound}}}^{{{upper_bound}}} {sp.latex(f_expr)} \, dx")
        
        # Display numerical result
        st.metric("Numerical Value", f"{float(integral_val):.4f}")
        
        with st.expander("See Symbolic Steps"):
            indefinite = sp.integrate(f_expr, x)
            st.write("Indefinite Integral:")
            st.latex(rf"{sp.latex(indefinite)} + C")

    with col2:
        # --- Plotting with Plotly ---
        x_vals = np.linspace(lower_bound - 2, upper_bound + 2, resolution)
        y_vals = f_num(x_vals)
        
        # Area under curve points
        x_fill = np.linspace(lower_bound, upper_bound, resolution)
        y_fill = f_num(x_fill)

        fig = go.Figure()

        # Main Function Line
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='#007BFF')))

        # Shaded Area
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_fill, x_fill[::-1]]),
            y=np.concatenate([y_fill, np.zeros_like(y_fill)]),
            fill='toself',
            fillcolor='rgba(0, 123, 255, 0.3)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name=f'Area: {float(integral_val):.2f}'
        ))

        fig.update_layout(
            title=f"Visualization of f(x) = {func_input}",
            xaxis_title="x",
            yaxis_title="f(x)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: Could not parse function. Please use Python math syntax (e.g., `x**2` for $x^2$).")
    st.info("Tip: Use `*` for multiplication and `**` for powers.")
