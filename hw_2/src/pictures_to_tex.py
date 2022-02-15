def convert_picture_to_tex(filename: str) -> str:
    return "\\begin{figure}\n\\centering\n\\includegraphics[width=\\textwidth]{" + filename + "}\n\\end{figure}\n"
