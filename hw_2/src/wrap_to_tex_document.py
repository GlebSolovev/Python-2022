def wrap_into_tex_document(tex_body: str) -> str:
    header = r"""\documentclass[12pt]{article}
\usepackage[T1, T2A]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english,russian]{babel}
\usepackage{tabularx}
\usepackage{graphicx}
\usepackage[a4paper,left=15mm,right=15mm,top=30mm,bottom=20mm]{geometry}
\parindent=0mm
\parskip=3mm
\pagestyle{empty}

\begin{document}
\thispagestyle{empty}

"""
    footer = "\n\\end{document}"
    return header + tex_body + footer
