
# OSS Torch Connector

## Overview

OSS Torch Connector provides the following features:

- [Map-style and Iterable-style datasets](https://pytorch.org/docs/stable/data.html#dataset-types): For loading datasets from OSS for model training.[Examples](https://aliyun.github.io/oss-connector-for-ai-ml/#/torchconnector/examples?id=dataset)

- checkpoints: For saving and loading checkpoints to/from OSS. [Examples](https://aliyun.github.io/oss-connector-for-ai-ml/#/torchconnector/examples?id=checkpoint)

- [Distributed Checkpoints(DCP)](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html): For saving and loading DCP to and from OSS. [Examples](https://aliyun.github.io/oss-connector-for-ai-ml/#/torchconnector/examples?id=distributed-checkpoints)

- safetensors: For directly loading tensors from safetensors files on OSS, or saving tensors directly to safetensors files on OSS. [Examples](https://aliyun.github.io/oss-connector-for-ai-ml/#/torchconnector/examples?id=safetensor)

The core part of is OSS Connector for AI/ML is implemented in C++ using [PhotonLibOS](https://github.com/alibaba/PhotonLibOS). This repository only contains the code of Python.


## Related

[中文文档: 使用OSS Connector for AI/ML加速模型训练](https://help.aliyun.com/zh/oss/developer-reference/oss-connector-overview)
