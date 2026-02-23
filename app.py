import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import subprocess
import os

st.set_page_config(page_title="Dynamic Integral Master", layout="wide")
st.title("∫ Dynamic Integral & LaTeX Generator")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Parameters")
func_str = st.sidebar.text_input("Enter f(x):", value="sqrt(x**2 - 1)")
lower_bound = st.sidebar.number_input("Lower Bound (a)", value=1.0, step=0.5)
upper_bound = st.sidebar.number_input("Upper Bound (b)", value=5.0, step=0.5)

try:
    # 1. Parse and Compute
    x = sp.symbols('x')
    clean_expr = func_str.replace('^', '**')
    f_expr = sp.parse_expr(clean_expr, transformations='all')

    # 2. Integrate and SIMPLIFY (This fixes the messy unsimplified outputs!)
    raw_indefinite = sp.integrate(f_expr, x)
    F_expr = sp.simplify(raw_indefinite) # Force algebraic simplification
    
    definite_integral_raw = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    numerical_value = float(sp.re(definite_integral_raw.evalf()))

    # Evaluate bounds on the simplified function
    F_b = F_expr.subs(x, upper_bound).evalf()
    F_a = F_expr.subs(x, lower_bound).evalf()

    # --- UI Display ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("📝 Calculus Steps")
        st.latex(rf"f(x) = {sp.latex(f_expr)}")
        
        with st.expander("Show Simplified Antiderivative F(x)"):
            st.latex(sp.latex(F_expr))
            
        st.write("**Fundamental Theorem (FTC):**")
        st.latex(rf"F({upper_bound}) = {float(sp.re(F_b)):.4f}")
        st.latex(rf"F({lower_bound}) = {float(sp.re(F_a)):.4f}")
        st.success(f"**Result:** {numerical_value:.5f}")

        # --- Dynamic LaTeX Generation ---
        if st.button("⚙️ Compile PDF Report"):
            with st.spinner("Writing and compiling LaTeX..."):
                # Safely format SymPy outputs to LaTeX strings
                latex_f = sp.latex(f_expr)
                latex_F = sp.latex(F_expr)
                latex_Fb = sp.latex(F_b)
                latex_Fa = sp.latex(F_a)
                
                # Construct the raw LaTeX document
                tex_content = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{geometry}
\geometry{margin=1in}

\begin{document}

\begin{center}
    \Large \textbf{Integral Evaluation Report}
\end{center}

\vspace{0.5cm}
\textbf{1. The Definite Integral Setup:}
\[ I = \int_{""" + str(lower_bound) + r"""}^{""" + str(upper_bound) + r"""} """ + latex_f + r""" \, dx \]

\textbf{2. Finding the Antiderivative $F(x)$:}
Using symbolic integration and algebraic simplification:
\[ F(x) = \int """ + latex_f + r""" \, dx = """ + latex_F + r""" + C \]

\textbf{3. Applying the Fundamental Theorem of Calculus:}
\[ \int_{""" + str(lower_bound) + r"""}^{""" + str(upper_bound) + r"""} f(x) \, dx = F(""" + str(upper_bound) + r""") - F(""" + str(lower_bound) + r""") \]

Evaluating at the upper bound $x = """ + str(upper_bound) + r"""$:
\[ F(""" + str(upper_bound) + r""") = """ + latex_Fb + r""" \]

Evaluating at the lower bound $x = """ + str(lower_bound) + r"""$:
\[ F(""" + str(lower_bound) + r""") = """ + latex_Fa + r""" \]

\textbf{4. Final Result:}
\[ I = """ + f"{numerical_value:.5f}" + r""" \]

\end{document}
"""
                # Save the .tex file
                with open("solution.tex", "w", encoding="utf-8") as f:
                    f.write(tex_content)
                
                # Run pdflatex and capture errors
                try:
                    result = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", "solution.tex"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True,
                        check=True
                    )
                    
                    with open("solution.pdf", "rb") as f:
                        pdf_data = f.read()
                        
                    st.success("PDF compiled successfully!")
                    st.download_button("📥 Download LaTeX PDF", data=pdf_data, file_name="integral_report.pdf", mime="application/pdf")
                    
                except subprocess.CalledProcessError as e:
                    st.error("LaTeX Compilation Failed (exit status 1).")
                    with st.expander("View LaTeX Error Log"):
                        # This will show you exactly what caused pdflatex to crash!
                        st.code(e.stdout, language="text")
                    
                    st.download_button("📥 Download Raw .tex File Instead", data=tex_content, file_name="solution.tex", mime="text/plain")

    # --- Plotting ---
    with col1:
        st.subheader("📊 Function Graph")
        x_plot = np.linspace(lower_bound - 1, upper_bound + 1, 400)
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

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_plot, y=y_plot, mode='lines', name='f(x)', line=dict(color='#007BFF', width=3)))
        fig.update_layout(title="Area Visualization", template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")

# Cleanup temp files
for file in ["solution.tex", "solution.aux", "solution.log"]:
    if os.path.exists(file):
        os.remove(file)
