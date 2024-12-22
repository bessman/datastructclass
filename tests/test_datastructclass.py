from dataclasses import is_dataclass
from struct import Struct
from typing import Annotated

import pytest

from datastructclass import DataStructClass

UINT8 = Annotated[int, Struct("=B")]
INT16 = Annotated[int, Struct("=h")]
DOUBLE = Annotated[float, Struct("=d")]


class Person(DataStructClass):
    name: Annotated[bytes, Struct("=8s")]
    age: UINT8
    id_no: INT16
    height: DOUBLE
    accounts: Annotated[list[int], Struct("=4I")]


anna = Person(
    name=b"Anna    ", age=31, id_no=1115, height=1.76, accounts=[22, 33, 44, 55]
)
anna_packed = (
    b"Anna    \x1f[\x04)\\\x8f\xc2\xf5(\xfc?\x16"
    + b"\x00\x00\x00!\x00\x00\x00,\x00\x00\x007\x00\x00\x00"
)


def test_pack():
    assert anna.pack() == anna_packed


def test_bytes():
    assert anna.pack() == bytes(anna)


def test_unpack():
    assert Person.unpack(anna_packed) == anna


def test_pack_unpack():
    assert Person.unpack(anna.pack()) == anna


def test_is_dataclass():
    assert is_dataclass(anna)


def test_missing_metadata():
    with pytest.raises(TypeError):

        class BadPerson(DataStructClass):
            age: int
