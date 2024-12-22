"""A DataStructClass is a dataclass with struct-like semantics for serialization."""

import struct
import sys
from collections.abc import Iterable
from dataclasses import astuple, dataclass, fields
from itertools import islice
from struct import Struct
from typing import ClassVar

if sys.version_info >= (3, 11):
    from typing import Self, dataclass_transform
else:
    from typing import Any, Callable, TypeVar

    Self = Any
    _T = TypeVar("_T")

    def dataclass_transform() -> Callable[[_T], _T]:
        """Noop decorator to support <python3.11."""

        def decorator(cls_or_fn: Callable[[_T], _T]) -> Callable[[_T], _T]:
            return cls_or_fn

        return decorator


__version__ = "0.1.0"


@dataclass
@dataclass_transform()
class DataStructClass:
    """A dataclass with struct-like semantics.

    Subclasses of this class are dataclasses, with the following additional features:

        <class>.format
        <class>.size
        <class>.unpack
        <instance>.pack
        <instance.__bytes__>

    Each member of a DataStructClass must provide struct metadata via typing.Annotated,
    for example:

    class MyDSC(DataStructClass):
        member_a: Annotated[int, struct.Struct("L")]  # member_a is an unsigned long.
        member_b: Annotated[float, struct.Struct("d")]  # member_b is a double.
    """

    _annotations: ClassVar[list[tuple[type, Struct]]]
    format: ClassVar[list[str]]
    size: ClassVar[int]

    def __init_subclass__(cls: type[Self]) -> None:
        """Create serializer from member metadata.

        Raises
        ------
        TypeError
            If any non-ClassVar member is missing struct metadata.
        """
        dataclass(cls)
        cls._annotations = []

        try:
            for f in fields(cls):
                assert hasattr(f.type, "__metadata__")
                assert hasattr(f.type, "__origin__")
                metadata = f.type.__metadata__
                struct_metadata = filter(lambda m: isinstance(m, Struct), metadata)
                cls._annotations.append((f.type.__origin__, next(struct_metadata)))
        except (AssertionError, AttributeError, StopIteration) as exc:
            msg = f"Field '{f.name}' missing Struct metadata"
            raise TypeError(msg) from exc

        serializers = [ser for _, ser in cls._annotations]
        cls.format = [s.format for s in serializers]
        cls.size = sum(s.size for s in serializers)

    def pack(self: Self) -> bytes:
        """See DataStructClass.__bytes__."""
        return bytes(self)

    @classmethod
    def unpack(cls: type[Self], buffer: bytes) -> Self:
        """Unpack bytes to a DataStructClass.

        Parameters
        ----------
        buffer : bytes
            Data to unpack.

        Raises
        ------
        struct.error
            If the buffer size is not equal to the class' size attribute.

        Returns
        -------
        DataStructClass
            An instance of a DataStructClass containing the data represented by the
            input bytes.
        """
        if len(buffer) != cls.size:
            msg = (
                f"{cls.unpack} ({cls.format}) requires {cls.size} bytes, got "
                f"{len(buffer)}"
            )
            raise struct.error(msg)

        iterbuf = iter(buffer)
        args: list[int | tuple[int, ...] | bytes] = []

        for typ, ser in cls._annotations:
            arg = ser.unpack(bytes(islice(iterbuf, ser.size)))

            if isinstance(typ, Iterable):
                args += [typ(arg)]
            else:
                args += [typ(*arg)]

        return cls(*args)

    def __bytes__(self: Self) -> bytes:
        """Pack an instance of DataStructClass into a bytes representation.

        Returns
        -------
        bytes
            Raw bytes value representing the data held by the DataStructClass.
        """
        ret = b""

        for (typ, ser), val in zip(self._annotations, astuple(self)):
            ret += ser.pack(*val) if isinstance(typ, Iterable) else ser.pack(val)

        return ret
