import os
from typing import NoReturn
from fibs_ast_drawer.main import draw_fibs_ast

from hw_2.pictures_to_tex import convert_picture_to_tex
from hw_2.tables_to_tex import convert_tables_to_tex
from hw_2.wrap_to_tex_document import wrap_into_tex_document


def write_to_file(content: str, filename: str) -> NoReturn:
    with open(filename, "w") as file:
        file.write(content)


if __name__ == '__main__':
    draw_fibs_ast()

    test_simple_table = [[j * 5 + i + 1 for i in range(5)] for j in range(5)]
    test_long_sentences_table = [["word " * (j * 5 + i + 1) for i in range(5)] for j in range(5)]
    test_tables = [test_simple_table, test_long_sentences_table]

    tex_body = convert_tables_to_tex(test_tables) + "\n" + convert_picture_to_tex("artifacts/ast.png")
    tex_content = wrap_into_tex_document(tex_body)

    tex_filename = "artifacts/output.tex"
    os.makedirs(os.path.dirname(tex_filename), exist_ok=True)
    write_to_file(tex_content, tex_filename)
