from functools import partial
from typing import List, Any, Callable, Iterable, Union, Tuple
import io
import torch.utils.data
import uuid
import logging
import time
import os
import errno

from ._oss_client import OssClient, DataObject
from ._oss_bucket_iterable import OssBucketIterable, identity, parse_oss_uri
from ._oss_tar_iterable import OssTarIterable

log = logging.getLogger(__name__)

class OssMapDataset(torch.utils.data.Dataset):
    """A Map-Style dataset created from OSS objects.

    To create an instance of OssMapDataset, you need to use
    `from_prefix`, `from_objects`, `from_manifest_file` or `from_tar` methods.
    """

    def __init__(
        self,
        endpoint: str,
        cred_path: str,
        config_path: str,
        get_dataset_objects: Callable[[OssClient], Iterable[DataObject]],
        transform: Callable[[DataObject], Any] = identity,
        tar_uri: str = None,
        tar_index_uri: str = None,
        cred_provider: Any = None,
    ):
        self._uuid = uuid.uuid4()
        self._endpoint = endpoint
        log.info("OssMapDataset init, uuid: %s, endpoint: %s", self._uuid, self._endpoint)
        init_time = time.time()
        if not endpoint:
            raise ValueError("endpoint must be non-empty")
        if not cred_path:
            self._cred_path = ""
        else:
            self._cred_path = cred_path
        self._cred_provider = cred_provider
        if not config_path:
            self._config_path = ""
        else:
            self._config_path = config_path
        self._get_dataset_objects = get_dataset_objects
        self._transform = transform
        self._client = OssClient(self._endpoint, self._cred_path, self._config_path, self._uuid, cred_provider=self._cred_provider)
        self._client_pid = os.getpid()
        self._from_tar = False
        if tar_uri and tar_index_uri:
            tar_bucket, tar_key = parse_oss_uri(tar_uri)
            index_bucket, index_key = parse_oss_uri(tar_index_uri)
            if tar_bucket != index_bucket:
                raise ValueError("tar_uri and tar_index_uri must be in the same bucket")
            self._from_tar = True
            self._tar_bucket = tar_bucket
            self._tar_key = tar_key
            self._tar_index_key = index_key
            self._bucket_objects = self._get_dataset_objects(self._client)
        else:
            self._bucket_objects = list(self._get_dataset_objects(self._client))
        log.info("OssMapDataset init done, uuid: %s, time cost: %.2f s", self._uuid, time.time() - init_time)


    @property
    def _dataset_bucket_objects(self) -> List[DataObject]:
        if self._bucket_objects is None:
            self._bucket_objects = list(self._get_dataset_objects(self._get_client()))
            log.info("OssMapDataset get bucket objects")
        return self._bucket_objects

    @classmethod
    def from_objects(
        cls,
        object_uris: Union[str, Iterable[str]],
        endpoint: str,
        *,
        cred_path: str = "",
        cred_provider: Any = None,
        config_path: str = "",
        transform: Callable[[DataObject], Any] = identity,
    ):
        """Returns an instance of OssMapDataset using the OSS URI(s) provided.

        Args:
          object_uris(str | Iterable[str]): OSS URI of the object(s) desired.
          endpoint(str): Endpoint of the OSS bucket where the objects are stored.
          cred_path(str): Credential info of the OSS bucket where the objects are stored.
          config_path(str): Configuration file path of the OSS connector.
          transform: Optional callable which is used to transform an DataObject into the desired type.
          cred_provider: OSS credential provider.

        Returns:
            OssMapDataset: A Map-Style dataset created from OSS objects.
        """
        log.info(f"Building {cls.__name__} from_objects")
        return cls(
            endpoint, cred_path, config_path, partial(OssBucketIterable.from_uris, object_uris, preload=False),
            transform=transform, cred_provider=cred_provider
        )

    @classmethod
    def from_prefix(
        cls,
        oss_uri: str,
        endpoint: str,
        *,
        cred_path: str = "",
        cred_provider: Any = None,
        config_path: str = "",
        transform: Callable[[DataObject], Any] = identity,
    ):
        """Returns an instance of OssMapDataset using the OSS URI provided.

        Args:
          oss_uri(str): An OSS URI (prefix) of the object(s) desired. Objects matching the prefix will be included in the returned dataset.
          endpoint(str): Endpoint of the OSS bucket where the objects are stored.
          cred_path(str): Credential info of the OSS bucket where the objects are stored.
          config_path(str): Configuration file path of the OSS connector.
          transform: Optional callable which is used to transform an DataObject into the desired type.
          cred_provider: OSS credential provider.

        Returns:
            OssMapDataset: A Map-Style dataset created from OSS objects.
        """
        log.info(f"Building {cls.__name__} from_prefix")
        return cls(
            endpoint, cred_path, config_path, partial(OssBucketIterable.from_prefix, oss_uri, preload=False),
            transform=transform, cred_provider=cred_provider
        )

    @classmethod
    def from_manifest_file(
        cls,
        manifest_file_path: str,
        manifest_parser: Callable[[io.IOBase], Iterable[Tuple[str, str]]],
        oss_base_uri: str,
        endpoint: str,
        *,
        cred_path: str = "",
        cred_provider: Any = None,
        config_path: str = "",
        transform: Callable[[DataObject], Any] = identity,
    ):
        """Returns an instance of OssMapDataset using manifest file provided.

        Args:
          manifest_file_path(str): OSS URI or local path of manifest file.
          manifest_parser: A callable which takes an io.IOBase object and returns an iterable of (object_uri, label).
          oss_base_uri(str): The base URI of the OSS object in manifest file.
          endpoint(str): Endpoint of the OSS bucket where the objects are stored.
          cred_path(str): Credential info of the OSS bucket where the objects are stored.
          config_path(str): Configuration file path of the OSS connector.
          transform: Optional callable which is used to transform an DataObject into the desired type.
          cred_provider: OSS credential provider.

        Returns:
            OssMapDataset: A Map-Style dataset created from OSS objects.
        """
        log.info(f"Building {cls.__name__} from_manifest_file")
        return cls(
            endpoint, cred_path, config_path, partial(OssBucketIterable.from_manifest_file, manifest_file_path, manifest_parser, oss_base_uri, preload=False),
            transform=transform, cred_provider=cred_provider
        )

    @classmethod
    def from_tar(
        cls,
        tar_uri: str,
        tar_index_uri: str,
        endpoint: str,
        *,
        cred_path: str = "",
        cred_provider: Any = None,
        config_path: str = "",
        transform: Callable[[DataObject], Any] = identity,
    ):
        """Returns an instance of OssMapDataset using tar file provided.

        Args:
          tar_uri(str): OSS URI of tar archive.
          tar_index_uri(str): OSS URI of tar index file corresponding to tar archive.
          endpoint(str): Endpoint of the OSS bucket where the objects are stored.
          cred_path(str): Credential info of the OSS bucket where the objects are stored.
          config_path(str): Configuration file path of the OSS connector.
          transform: Optional callable which is used to transform an DataObject into the desired type.
          cred_provider: OSS credential provider.

        Returns:
            OssMapDataset: An Map-Style dataset created from tar file.
        """
        log.info(f"Building {cls.__name__} from_tar")
        return cls(
            endpoint, cred_path, config_path, partial(OssTarIterable.from_tar, tar_uri, tar_index_uri, preload=False),
            transform=transform, cred_provider=cred_provider, tar_uri=tar_uri, tar_index_uri=tar_index_uri
        )

    def _get_client(self):
        if self._client is None:
            self._client = OssClient(self._endpoint, self._cred_path, self._config_path, self._uuid)
            log.info("OssMapDataset new client")
        if self._client_pid != os.getpid():
            worker_info = torch.utils.data.get_worker_info()
            if worker_info is not None:
                # reset client id
                self._client._id = worker_info.id
                self._client._total = worker_info.num_workers
            self._client_pid = os.getpid()
        return self._client

    def _get_transformed_object_safe(self, object: DataObject) -> Any:
        eno = object.err()
        if eno != 0:
            errstr = "failed to get next object, errno=%d(%s), msg=%s" % (eno, os.strerror(eno), object.error_msg())
            log.error("OssMapDataset get item %s faild: %s", object.key, errstr)
            if eno == errno.ENOENT:
                return self._transform(None)
            else:
                raise RuntimeError(errstr)
        return self._transform(object)

    def __getitem__(self, i: int) -> Any:
        if not self._from_tar:
            object = self._dataset_bucket_objects[i]
            log.debug("OssMapDataset get item [%d], key: %s, size: %d, label: %s", i, object.key, object.size, object.label)
            bucket, key = parse_oss_uri(object.key)
            if object.size <= 0:
                new_object = self._get_client().get_object(bucket, key, 0, label=object.label, type=2)           # mem
            else:
                new_object = self._get_client().get_object(bucket, key, object.size, label=object.label, type=0) # basic
        else:
            new_object = self._get_client().get_object(bucket=self._tar_bucket, key=self._tar_key, size=i,
                                                       label=self._tar_index_key, type=3)                        # tar
        return self._get_transformed_object_safe(new_object)

    def __getitems__(self, indices: List[int]) -> List[Any]:
        log.debug("OssMapDataset get items %s", indices)
        if not self._from_tar:
            objects = [self._dataset_bucket_objects[i] for i in indices]
            iter = self._get_client().list_objects_from_uris(objects, prefetch=True, include_errors=True)
            # should return list, default collate needs batch be subscriptable
            return [self._get_transformed_object_safe(object) for object in iter]
        else:
            if self.is_continuous(indices):
                log.debug("OssMapDataset get items, start: %d, length: %d", indices[0], len(indices))
                iter = self._get_client().list_objects_from_tar(self._tar_bucket, self._tar_key, self._tar_index_key,
                                                                [indices[0]], [len(indices)], prefetch=True, include_errors=True)
                return [self._get_transformed_object_safe(object) for object in iter]
            else:
                iter = self._get_client().list_objects_from_tar(self._tar_bucket, self._tar_key, self._tar_index_key,
                                                                indices, [], prefetch=True, include_errors=True)
                return [self._get_transformed_object_safe(object) for object in iter]

    def __len__(self):
        size = len(self._dataset_bucket_objects)
        log.info("OssMapDataset get len (%d)", size)
        return size

    def is_continuous(self, indices):
        for i in range(1, len(indices)):
            if indices[i] - indices[i - 1] != 1:
                return False
        return True
