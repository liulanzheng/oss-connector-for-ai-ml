# Python API

## Overview

Users can create an OssModelConnector in Python and call its provided methods to access data on OSS. The OssModelConnector provides methods for read-only access to OSS, such as list, open, and read, but does not offer any write methods for now.

## Key Features

- List and FastList

    In addition to offering a normal list implementation, a faster method called "FastList" is also provided to significantly enhance the efficiency of listing a large number of objects. FastList achieves this by concurrently sending list requests and more intelligently handling the segmentation of lists, allowing the listing of millions of objects to be completed within seconds.

- Data Prefetching

    This optimization is specifically designed for large models. After the open api is called, the ModelConnector performs high-concurrency data prefetching according to the order of opening to fully leverage the bandwidth advantages of OSS. It temporarily stores the data in memory, allowing users to quickly load data from memory when reading.

## Main APIs

- Initialization

    To initialize an OssModelConnector, please refer to [configuration](./configuration.md)

    ```python
    connector = OssModelConnector(endpoint=ENDPOINT,
                                  cred_provider=EnvironmentVariableCredentialsProvider(),
                                  config_path='/tmp/config.json')
    ```

- List objects

    By passing in the `bucket` and `prefix`, users can obtain a list of all objects that meet the criteria, including name and size of objects.

    ```python
    objs = connector.list('ai-testset', "geonet/images/DISC/DISC.01/2022.001")
    for obj in objs:
        print(obj.key)
        print(obj.size)
    ```

    Do FastList by passing True in the second parameter, which works more faster for large amount objects.
    The order of objects obtained by FastList is not guaranteed. If a specific order is required, users can sort the result based on `key`.

    ```python
    objs = connector.list('ai-testset', "geonet/images/DISC/DISC.01/2022.001", True)
    ```

- Open object

    Open an object through a URI. The URI format is `oss://{bucket}/{name}`. For example, `oss://ai-testset/dir1/obj1` represents an object named `dir1/obj1` in the `ai-testset` bucket.

    The open function accepts two parameters: the first is the URI, and the second is binary, which is of type bool and defaults to True, indicating that the file will be opened in binary mode. If set to False, it will be opened in text mode.

    ```python
    # open as binary mode
    obj = connector.open('oss://ai-testset/dir1/obj1')

    # open as text mode
    obj1 = connector.open('oss://ai-testset/dir1/obj1', False)
    ```

    After calling open, OssModelConnector will start prefetching in the order of the open calls. For scenarios involving loading large model files in shards (e.g. model-00001-of-00038.safetensors to model-00038-of-00038.safetensors), we recommend making sequential batch calls to open first, and then reading each one individually."

- Read object data

    Read, readinto, seek methods are provided and they follow the standard usage of Python streams.

    When a read call is made, if the data has already been prefetched into memory, it is returned directly from memory. Otherwise, a request is sent to OSS to retrieve and return the data.

    ```python
    # read whole data
    data = obj.read()

    # read a specified amount of data
    data = obj.read(4*1024*1024)

    # read into buffer
    buf = bytearray(4 * 1024 * 1024)
    obj.readinto(buf)

    # seek to a position
    obj.seek(0)
    ```

- Destroy object

    Destroying an object will release its occupied memory resources. Users can rely on Python's GC to handle it automatically, or perform manual destruction in memory-sensitive scenarios.


## Example

Below is a sample code for loading a model in multiple shards. First, open them to initiate prefetching, and then read them sequentially.

```python
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from ossmodelconnector import OssModelConnector

connector = OssModelConnector(endpoint=ENDPOINT,
                              cred_provider=EnvironmentVariableCredentialsProvider(),
                              config_path='/tmp/config.json')

objs = []
for i in range(1, 39): # 1-38
    name = f"oss://ai-testset/qwen/Qwen1.5-72B-Chat/model-{i:05d}-of-00038.safetensors"
    obj = connector.open(name)
    objs.append(obj)

# using read
for i in range(0, 38): # 0-37
    while True:
        data = objs[i].read(4*1024*1024)
        if not data:
            print("read object done ", i+1)
            break

# or using readinto (recommended)
buf = bytearray(4 * 1024 * 1024)
for i in range(0, 38): # 0-37
    objs[i].seek(0)
    while True:
        n = objs[i].readinto(buf)
        if n == 0:
            print("readinto object done ", i+1)
            break
```