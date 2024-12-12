from typing import List, Union, Any

class DataObject:
    key: str

    def __enter__(self) -> DataObject: ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...
    def tell(self) -> int: ...
    def seek(self, offset: int, whence: int) -> int: ...
    def read(self, count: int) -> bytes: ...
    def readinto(self, buf) -> int: ...
    def mmap(self) -> int: ...
    def close(self) -> int: ...
    def size(self) -> int: ...


class DataObjectInfo:
    key: str
    size: int


class Connector:
    def open(uri: str, prefetch: bool, userfault: bool, binary: bool) -> DataObject: ...
    def prepare_directory(uri: str, dir: str, libc: bool) -> int: ...
    def list(bucket: str, prefix: str, fast: bool) -> List[DataObjectInfo]: ...


def new_oss_connector(endpoint: str, cred: Union[str, Any], config_path: str) -> Connector:
    ...