"""TODO"""
from typing import Optional
import ctypes as c

from exonum_runtime.c_callbacks import allocate, free_resource
from .common import BinaryData

# When working with C, it's always a compromise.
# pylint: disable=protected-access


class RawListIndex(c.Structure):
    """TODO"""


class RawListIndexMethods(c.Structure):
    """TODO"""

    AllocateFunctype = c.CFUNCTYPE(c.POINTER(c.c_uint8), c.c_uint64)

    _fields_ = [
        ("get", c.CFUNCTYPE(BinaryData, c.POINTER(RawListIndex), c.c_uint64, AllocateFunctype)),
        ("push", c.CFUNCTYPE(None, c.POINTER(RawListIndex), BinaryData)),
        ("pop", c.CFUNCTYPE(BinaryData, c.POINTER(RawListIndex), AllocateFunctype)),
        ("len", c.CFUNCTYPE(c.c_uint64, c.POINTER(RawListIndex))),
    ]


RawListIndex._fields_ = [("fork", c.c_void_p), ("index_name", c.c_char_p), ("methods", RawListIndexMethods)]


class ListIndexWrapper:
    """TODO"""

    def __init__(self, inner: RawListIndex) -> None:
        self._inner = inner

    def get(self, idx: int) -> Optional[bytes]:
        """TODO"""
        result = self._inner.methods.get(self._inner, c.c_uint64(idx), allocate)

        if not result.data:
            return None

        data = result.data[: result.data.value]

        free_resource(result.data)

        return data

    def push(self, value: bytes) -> None:
        """TODO"""
        # mypy isn't a friend of ctypes
        data = BinaryData(c.cast(value, c.POINTER(c.c_uint8)), c.c_uint64(len(value)))  # type: ignore

        self._inner.methods.push(self._inner, data)

    def pop(self) -> Optional[bytes]:
        """TODO"""
        result = self._inner.methods.pop(self._inner, allocate)

        if not result.data:
            return None

        data = result.data[: result.data.value]

        free_resource(result.data)

        return data

    def len(self) -> int:
        """TODO"""
        result = self._inner.methods.len(self._inner)

        return result.value
