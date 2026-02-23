import streamlit as st
import subprocess
import os
import sympy as sp

# --- Page Config ---
st.set_page_config(page_title="LaTeX Integral Master", page_icon="∫", layout="wide")

st.title("∫ Rigorous Integral Calculator")
st.markdown("Generates mathematically rigorous, simplified step-by-step solutions compiled in LaTeX.")

# --- LaTeX Template ---
def generate_latex_content():
    # This is the proper, simplified step-by-step solution for sqrt(x^2 - 1)
    return r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{geometry}
\geometry{margin=1in}

\begin{document}

\begin{center}
    \Large \textbf{Step-by-Step Integral Evaluation}
\end{center}

\vspace{0.5cm}
\textbf{Evaluate the integral:}
$$ I = \int \sqrt{x^2 - 1} \, dx $$

\textbf{Solution:}

\textbf{Step 1: Trigonometric Substitution} \\
Let $x = \sec(\theta)$, which means $dx = \sec(\theta)\tan(\theta) \, d\theta$. \\
Substitute these into the integral:
$$ I = \int \sqrt{\sec^2(\theta) - 1} \cdot \sec(\theta)\tan(\theta) \, d\theta $$

\textbf{Step 2: Simplify using Pythagorean Identity} \\
Since $\sec^2(\theta) - 1 = \tan^2(\theta)$, the integral becomes:
$$ I = \int \sqrt{\tan^2(\theta)} \cdot \sec(\theta)\tan(\theta) \, d\theta $$
$$ I = \int \tan^2(\theta)\sec(\theta) \, d\theta $$

\textbf{Step 3: Integration by Parts} \\
We can rewrite the integral using $\tan^2(\theta) = \sec^2(\theta) - 1$:
$$ I = \int (\sec^3(\theta) - \sec(\theta)) \, d\theta $$
Using the standard reduction formulas for secant:
$$ \int \sec^3(\theta) \, d\theta = \frac{1}{2}\sec(\theta)\tan(\theta) + \frac{1}{2}\ln|\sec(\theta) + \tan(\theta)| $$
$$ \int \sec(\theta) \, d\theta = \ln|\sec(\theta) + \tan(\theta)| $$

Subtracting the two yields:
$$ I = \frac{1}{2}\sec(\theta)\tan(\theta) - \frac{1}{2}\ln|\sec(\theta) + \tan(\theta)| + C $$

\textbf{Step 4: Algebraic Back-Substitution} \\
Using our reference right triangle where $\sec(\theta) = x$, we know:
\begin{itemize}
    \item Hypotenuse = $x$
    \item Adjacent = $1$
    \item Opposite = $\sqrt{x^2 - 1}$
\end{itemize}
Therefore, $\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}} = \sqrt{x^2 - 1}$.

Substitute these algebraic terms back into the evaluated integral:
$$ I = \frac{1}{2}(x)(\sqrt{x^2 - 1}) - \frac{1}{2}\ln|x + \sqrt{x^2 - 1}| + C $$

\textbf{Final Answer:}
$$ \int \sqrt{x^2 - 1} \, dx = \frac{x\sqrt{x^2 - 1}}{2} - \frac{1}{2}\ln|x + \sqrt{x^2 - 1}| + C, \quad C \in \mathbb{R} $$

\end{document}
"""

# --- App UI ---
st.subheader("Evaluate: $\int \sqrt{x^2 - 1} \, dx$")

if st.button("⚙️ Generate LaTeX Solution PDF"):
    with st.spinner("Compiling LaTeX document..."):
        tex_content = generate_latex_content()
        
        # Write to a temporary .tex file
        with open("solution.tex", "w") as f:
            f.write(tex_content)
            
        # Compile via command line pdflatex
        try:
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "solution.tex"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Read the generated PDF
            with open("solution.pdf", "rb") as f:
                pdf_data = f.read()
                
            st.success("PDF compiled successfully!")
            st.download_button(
                label="📥 Download Mathematically Rigorous PDF",
                data=pdf_data,
                file_name="simplified_solution.pdf",
                mime="application/pdf"
            )
            
        except FileNotFoundError:
            st.error("LaTeX compiler (`pdflatex`) not found on this system.")
            st.info("If running locally, ensure MiKTeX or TeX Live is installed. If on Streamlit Cloud, add `texlive-latex-base` to a `packages.txt` file in your repo.")
            
            # Fallback: Let them download the raw .tex file
            st.download_button(
                label="📥 Download raw .tex file instead",
                data=tex_content,
                file_name="solution.tex",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Compilation Error: {e}")

# Cleanup temp files
for file in ["solution.tex", "solution.aux", "solution.log"]:
    if os.path.exists(file):
        os.remove(file)
