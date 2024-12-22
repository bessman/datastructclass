# datastructclass

A `DataStructClass` is a `dataclass` with struct-like semantics. It can be
serialized/deserialized to/from `bytes`.

A subclass of `DataStructClass` is a `dataclass`, with the following additional
features:

```python
<class>.format
<class>.size
<class>.unpack
<instance>.pack
<instance.__bytes__>
```

Each member of a `DataStructClass` must provide struct metadata via `typing.Annotated`.

## Example

```python
from struct import Struct
from typing import Annotated
from datastructclass import DataStructClass

class MyDSC(DataStructClass):
    # Unsigned long:
    member_a: Annotated[int, Struct("=L")]
    # Double:
    member_b: Annotated[float, Struct("=d")]
    # Array of signed long with length 4.
    member_c: Annotated[list[int], Struct("=4I")]
    # Array of char, aka. a string, with length 8:
    member_d: Annotated[bytes, Struct("=8s")]


data = MyDSC(4000, 3.14, [-2, -1, 0, 1], b"charlie  ")
# 'send_over_wire' could a network socket, a serial port, etc.
send_over_wire(data.pack())
```

## Limitations

`DataStructClass` cannot contain variable-length members.
