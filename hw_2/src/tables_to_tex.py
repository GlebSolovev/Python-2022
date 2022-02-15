from typing import List, Any


def convert_to_tex_row(row: List[Any]) -> str:
    return " & ".join(map(str, row)) + " \\\\\n"


def convert_to_tex_table(table: List[List[Any]]) -> str:
    header = "\\begin{center}\n\\begin{tabularx}{\\textwidth}{*{" + str(
        len(table)) + "}{|>{\\centering\\arraybackslash}X}|}\n\\hline\n"

    footer = "\\hline\n\\end{tabularx}\n\\end{center}\n"

    body = "\\hline\n".join(map(convert_to_tex_row, table))

    return header + body + footer


def convert_tables_to_tex(tables: List[List[List[Any]]]) -> str:
    return "\n".join(map(convert_to_tex_table, tables))