import copy
import os
from typing import NoReturn, Tuple, Union

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


def find_hash_collision(iters=int(1e6)) -> Union[Tuple[MyMatrix, MyMatrix], None]:
    np.random.seed(0)
    for _ in range(iters):
        lhs = MyMatrix(np.random.randint(0, 10, (10, 10)))
        rhs = MyMatrix(np.random.randint(0, 10, (10, 10)))
        if lhs != rhs and hash(lhs) == hash(rhs):
            return lhs, rhs
    return None


def create_hard_matrix_artifacts() -> NoReturn:
    matrix_a, matrix_c = find_hash_collision()
    matrix_b = MyMatrix(np.eye(10, dtype=int))
    matrix_d = copy.deepcopy(matrix_b)

    MyMatrix.clear_cache()
    ab_prod = matrix_a @ matrix_b
    cached_cd_prod = matrix_c @ matrix_d
    MyMatrix.clear_cache()
    real_cd_prod = matrix_c @ matrix_d

    if not ((hash(matrix_a) == hash(matrix_c)) and (matrix_a != matrix_c) and (matrix_b == matrix_d) and (
            ab_prod != real_cd_prod) and (ab_prod == cached_cd_prod)):
        print("Hard unexpectedly failed")
        return

    output_directory = "../artifacts/hard/"
    write_to_file(str(matrix_a), f"{output_directory}A.txt")
    write_to_file(str(matrix_b), f"{output_directory}B.txt")
    write_to_file(str(matrix_c), f"{output_directory}C.txt")
    write_to_file(str(matrix_d), f"{output_directory}D.txt")

    write_to_file(str(ab_prod), f"{output_directory}AB.txt")
    write_to_file(str(real_cd_prod), f"{output_directory}CD.txt")
    write_to_file(str(hash(ab_prod)) + "\n" + str(hash(real_cd_prod)), f"{output_directory}hash.txt")


if __name__ == '__main__':
    create_easy_matrix_artifacts()
    create_medium_matrix_artifacts()
    create_hard_matrix_artifacts()
