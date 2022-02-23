import os
from typing import NoReturn

import numpy as np

from numpy_matrix import NumpyMatrix
from my_matrix import MyMatrix


def write_to_file(content: str, filename: str) -> NoReturn:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(content)


def create_easy_matrix_artifacts() -> NoReturn:
    np.random.seed(0)
    matrix_a = MyMatrix(np.random.randint(0, 10, (10, 10)))
    matrix_b = MyMatrix(np.random.randint(0, 10, (10, 10)))

    output_directory = "../artifacts/easy/"
    write_to_file(str(matrix_a + matrix_b), f"{output_directory}matrix+.txt")
    write_to_file(str(matrix_a * matrix_b), f"{output_directory}matrix*.txt")
    write_to_file(str(matrix_a @ matrix_b), f"{output_directory}matrix@.txt")


def create_medium_matrix_artifacts() -> NoReturn:
    np.random.seed(0)
    matrix_a = NumpyMatrix(np.random.randint(0, 10, (10, 10)))
    matrix_b = NumpyMatrix(np.random.randint(0, 10, (10, 10)))

    output_directory = "../artifacts/medium/"
    (matrix_a + matrix_b).write_to_file(f"{output_directory}matrix+.txt")
    (matrix_a * matrix_b).write_to_file(f"{output_directory}matrix*.txt")
    (matrix_a @ matrix_b).write_to_file(f"{output_directory}matrix@.txt")


if __name__ == '__main__':
    create_easy_matrix_artifacts()
    create_medium_matrix_artifacts()
