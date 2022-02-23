import numbers
import os
from typing import NoReturn

import numpy as np


class StrMatrixMixin:
    def __init__(self):
        self._matrix = None

    def __str__(self) -> str:
        return "\n".join(map(lambda row: " | ".join(map(str, row)), self._matrix))


class WriteToFileMixin:
    def write_to_file(self, filename: str) -> NoReturn:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write(str(self))


class NdarrayError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PropertiesNdarrayMixin:
    def __init__(self):
        self._ndarray = None

    @property
    def rows(self) -> int:
        return self._ndarray.shape[0]

    @property
    def cols(self) -> int:
        return self._ndarray.shape[1]

    @property
    def matrix(self) -> np.ndarray:
        return self._ndarray

    @matrix.setter
    def matrix(self, new_matrix):
        self._ndarray = np.asarray(new_matrix)
        if self._ndarray.ndim < 2:
            raise NdarrayError(
                f"matrix setter failed: not enough dims in np.asarray(new_matrix) = {self._ndarray.ndim}")


class NumpyMatrix(np.lib.mixins.NDArrayOperatorsMixin, StrMatrixMixin, WriteToFileMixin, PropertiesNdarrayMixin):
    def __init__(self, ndarray_matrix):
        super().__init__()
        self.ndarray_matrix = np.asarray(ndarray_matrix)
        self.matrix = ndarray_matrix  # check dims in mixin setter
        self._matrix = self.ndarray_matrix

    _HANDLED_TYPES = (np.ndarray, numbers.Number)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        out = kwargs.get('out', ())

        # do operations only with supported types
        for x in inputs + out:
            if not isinstance(x, self._HANDLED_TYPES + (NumpyMatrix,)):
                return NotImplemented

        # unpack
        inputs = tuple(x.ndarray_matrix if isinstance(x, NumpyMatrix) else x
                       for x in inputs)
        if out:
            kwargs['out'] = tuple(
                x.ndarray_matrix if isinstance(x, NumpyMatrix) else x
                for x in out)
        result = getattr(ufunc, method)(*inputs, **kwargs)

        if type(result) is tuple:
            return tuple(type(self)(x) for x in result)
        elif method == 'at':
            return None
        else:
            return type(self)(result)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.ndarray_matrix)
