from __future__ import annotations

import copy
from typing import NoReturn


class HashEqMatrixMixin:
    def __init__(self):
        self.matrix = None
        self.rows = None
        self.cols = None
        self.modulo = 103

    def __hash__(self) -> int:
        """
        Computes hash using built-in hash for tuple of inner matrix hash, rows and cols,
        then takes it modulo self.modulo;
        inner matrix hash computes as sum of elements of matrix modulo self.modulo.
        """
        matrix_hash = 0
        for row in self.matrix:
            for el in row:
                matrix_hash += el
            matrix_hash %= self.modulo
        return hash((matrix_hash, self.rows, self.cols)) % self.modulo

    def __eq__(self, other) -> bool:
        matrix_eq = self.matrix == other.matrix
        if not isinstance(matrix_eq, bool):
            matrix_eq = matrix_eq.all()
        return self.rows == other.rows and self.cols == other.cols and matrix_eq


class MyMatrixError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidDimensionsInitError(MyMatrixError):
    def __init__(self, cause: str = "unknown"):
        super().__init__("can't init MyMatrix: invalid dimensions; cause: " + cause)


class AddError(MyMatrixError):
    def __init__(self, cause: str = "unknown"):
        super().__init__("MyMatrix add is invalid, cause: " + cause)


class ElementWiseMultiplyError(MyMatrixError):
    def __init__(self, cause: str = "unknown"):
        super().__init__("MyMatrix element-wise multiply is invalid, cause: " + cause)


class MathematicalMultiplyError(MyMatrixError):
    def __init__(self, cause: str = "unknown"):
        super().__init__("MyMatrix mathematical multiply is invalid, cause: " + cause)


class MyMatrix(HashEqMatrixMixin):
    matmul_cache = {}

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix

        self.rows = len(matrix)
        if self.rows == 0:
            raise InvalidDimensionsInitError("zero rows")
        self.cols = len(matrix[0])
        if self.cols == 0:
            raise InvalidDimensionsInitError("zero cols")

        for index, row in enumerate(matrix):
            if len(row) != self.rows:
                raise InvalidDimensionsInitError(f"len(row[{index}]) != len(row[0])")

    def __str__(self) -> str:
        return "\n".join(map(lambda row: " | ".join(map(str, row)), self.matrix))

    def __add__(self, other) -> MyMatrix:  # +
        if not isinstance(other, MyMatrix):
            raise AddError(f"rhs must be MyMatrix, not {type(other)} object")
        if self.cols != other.cols or self.rows != other.rows:
            raise AddError(f"bad dimensions, ({self.cols}, {self.rows}) != ({other.cols}, {other.rows})")

        result_matrix = copy.deepcopy(self.matrix)
        for i in range(self.rows):
            for j in range(self.cols):
                result_matrix[i][j] += other.matrix[i][j]
        return MyMatrix(result_matrix)

    def __mul__(self, other) -> MyMatrix:  # *
        if not isinstance(other, MyMatrix):
            raise ElementWiseMultiplyError(f"rhs must be MyMatrix, not {type(other)} object")
        if self.cols != other.rows:
            raise ElementWiseMultiplyError(
                f"bad dimensions, ({self.cols}, {self.rows}) != ({other.cols}, {other.rows})")

        result_matrix = copy.deepcopy(self.matrix)
        for i in range(self.rows):
            for j in range(self.cols):
                result_matrix[i][j] *= other.matrix[i][j]
        return MyMatrix(result_matrix)

    def __matmul__(self, other) -> MyMatrix:  # @
        if not isinstance(other, MyMatrix):
            raise MathematicalMultiplyError(f"rhs must be MyMatrix, not {type(other)} object")
        if self.cols != other.rows:
            raise MathematicalMultiplyError(f"bad dimensions, lhs.cols ({self.cols}) != rhs.rows ({other.rows})")

        cache_key = (hash(self), hash(other))
        cache_result = MyMatrix.matmul_cache.get(cache_key, None)
        if cache_result is not None:
            return cache_result

        result_matrix = [[0 for _ in range(other.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for k in range(self.cols):
                for j in range(other.cols):
                    result_matrix[i][j] += self.matrix[i][k] * other.matrix[k][j]
        result = MyMatrix(result_matrix)

        MyMatrix.matmul_cache[cache_key] = result
        return result

    @staticmethod
    def clear_cache() -> NoReturn:
        MyMatrix.matmul_cache = {}
