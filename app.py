import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import subprocess
import os

st.set_page_config(page_title="Dynamic Integral Master", layout="wide")
st.title("∫ Dynamic Step-by-Step Integral Calculator")

# --- Step-by-Step Rule Parser ---
# This function hacks into SymPy's manual integrator to extract human-like steps
def generate_step_latex(expr, x_var):
    try:
        from sympy.integrals.manualintegrate import integral_steps
        rule_tree = integral_steps(expr, x_var)
        steps_latex = []
        
        # Recursive function to walk through SymPy's rule tree
        def walk(rule):
            if rule is None: return
            r_name = rule.__class__.__name__
            
            if r_name == 'AddRule':
                steps_latex.append(r"\item \textbf{Linearity Rule:} Break the integral into separate parts and evaluate them individually.")
                for sub in rule.substeps: walk(sub)
            elif r_name == 'URule':
                u_str = sp.latex(rule.u_func)
                steps_latex.append(rf"\item \textbf{U-Substitution:} Let $u = {u_str}$. Substitute $u$ and $du$ into the integral.")
                walk(rule.substep)
            elif r_name == 'PartsRule':
                u_str = sp.latex(rule.u)
                dv_str = sp.latex(rule.dv)
                steps_latex.append(rf"\item \textbf{Integration by Parts:} Let $u = {u_str}$ and $dv = {dv_str} \, dx$. Apply the formula $\int u \, dv = uv - \int v \, du$.")
                walk(rule.v_step)
                walk(rule.second_step)
            elif r_name == 'ConstantTimesRule':
                c_str = sp.latex(rule.constant)
                steps_latex.append(rf"\item \textbf{Constant Multiple:} Factor out the constant ${c_str}$ from the integral.")
                walk(rule.substep)
            elif r_name == 'PowerRule':
                steps_latex.append(r"\item \textbf{Power Rule:} Apply the power rule for integration: $\int x^n \, dx = \frac{x^{n+1}}{n+1}$.")
            elif r_name == 'TrigRule':
                steps_latex.append(r"\item \textbf{Trigonometric Identity:} Evaluate using standard trigonometric integral formulas.")
            elif r_name == 'TrigSubstitutionRule':
                theta = sp.latex(rule.theta)
                func = sp.latex(rule.func)
                steps_latex.append(rf"\item \textbf{Trig Substitution:} Use a trigonometric substitution (e.g., $x = f(\theta)$) to eliminate the radical.")
                walk(rule.substep)
            elif r_name == 'AlternativeRule':
                # SymPy tries multiple paths; we only want the one that worked
                if hasattr(rule, 'alternatives') and rule.alternatives:
                    walk(rule.alternatives[0])
            else:
                # Catch-all for basic rules
                clean_name = r_name.replace('Rule', '')
                steps_latex.append(rf"\item \textbf{{{clean_name} Applied:}} Evaluate the resulting expression.")
                if hasattr(rule, 'substep'): walk(rule.substep)

        walk(rule_tree)
        
        # Remove duplicate steps if the tree nested too deeply
        clean_steps = []
        for s in steps_latex:
            if not clean_steps or clean_steps[-1] != s:
                clean_steps.append(s)
                
        if not clean_steps:
            return r"\item \textbf{Direct Integration:} The antiderivative was found directly using standard integral tables."
            
        return "\n".join(clean_steps)
        
    except Exception as e:
        return r"\item \textbf{Algebraic Processing:} The steps for this specific function rely on complex internal algorithms rather than standard elementary rules."

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Parameters")
func_str = st.sidebar.text_input("Enter f(x):", value="x * exp(x)")
lower_bound = st.sidebar.number_input("Lower Bound (a)", value=0.0, step=0.5)
upper_bound = st.sidebar.number_input("Upper Bound (b)", value=2.0, step=0.5)

try:
    # 1. Parse and Compute
    x = sp.symbols('x')
    clean_expr = func_str.replace('^', '**')
    f_expr = sp.parse_expr(clean_expr, transformations='all')

    # 2. Integrate and Simplify
    raw_indefinite = sp.integrate(f_expr, x)
    F_expr = sp.simplify(raw_indefinite) 
    
    definite_integral_raw = sp.integrate(f_expr, (x, lower_bound, upper_bound))
    numerical_value = float(sp.re(definite_integral_raw.evalf()))

    F_b = F_expr.subs(x, upper_bound).evalf()
    F_a = F_expr.subs(x, lower_bound).evalf()

    # --- UI Display ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("📝 Calculus Logic")
        st.latex(rf"f(x) = {sp.latex(f_expr)}")
        
        with st.expander("Show Antiderivative F(x)"):
            st.latex(sp.latex(F_expr))
            
        st.write("**Evaluate Bounds:**")
        st.latex(rf"F({upper_bound}) = {float(sp.re(F_b)):.4f}")
        st.latex(rf"F({lower_bound}) = {float(sp.re(F_a)):.4f}")
        st.success(f"**Result:** {numerical_value:.5f}")

        # --- Dynamic LaTeX Generation ---
        if st.button("⚙️ Compile PDF Report"):
            with st.spinner("Analyzing steps and compiling LaTeX..."):
                
                # Extract the dynamic steps
                dynamic_steps_latex = generate_step_latex(f_expr, x)
                
                latex_f = sp.latex(f_expr)
                latex_F = sp.latex(F_expr)
                latex_Fb = sp.latex(F_b)
                latex_Fa = sp.latex(F_a)
                
                # Construct the LaTeX document with the new steps section
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

\textbf{2. Step-by-Step Breakdown:}
\begin{itemize}
""" + dynamic_steps_latex + r"""
\end{itemize}

\textbf{3. The Antiderivative $F(x)$:}
After applying the steps and simplifying algebraically:
\[ F(x) = """ + latex_F + r""" + C \]

\textbf{4. Applying the Fundamental Theorem of Calculus:}
\[ \int_{a}^{b} f(x) \, dx = F(b) - F(a) \]

Evaluating at the upper bound $x = """ + str(upper_bound) + r"""$:
\[ F(""" + str(upper_bound) + r""") = """ + latex_Fb + r""" \]

Evaluating at the lower bound $x = """ + str(lower_bound) + r"""$:
\[ F(""" + str(lower_bound) + r""") = """ + latex_Fa + r""" \]

\textbf{5. Final Result:}
\[ I = """ + f"{numerical_value:.5f}" + r""" \]

\end{document}
"""
                with open("solution.tex", "w", encoding="utf-8") as f:
                    f.write(tex_content)
                
                try:
                    subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", "solution.tex"], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                    )
                    with open("solution.pdf", "rb") as f:
                        pdf_data = f.read()
                        
                    st.success("PDF compiled successfully!")
                    st.download_button("📥 Download Step-by-Step PDF", data=pdf_data, file_name="integral_report.pdf", mime="application/pdf")
                    
                except subprocess.CalledProcessError as e:
                    st.error("LaTeX Compilation Failed.")
                    with st.expander("View Error Log"):
                        st.code(e.stdout, language="text")

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

for file in ["solution.tex", "solution.aux", "solution.log"]:
    if os.path.exists(file):
        os.remove(file)
