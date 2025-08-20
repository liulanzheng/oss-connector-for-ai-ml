# OSS Connector for AI/ML

[ossconnector.github.io](https://ossconnector.github.io/)

## Overview

OSS Connector for AI/ML contains some high-performance Python libraries specifically designed for AI and ML scenariosis, tailored to work with [Alibaba Cloud OSS (Object Storage Service)](https://www.alibabacloud.com/en/product/object-storage-service).

Currently, the OSS connector is composed of two libraries: OSS Model Connector and OSS Torch Connector.

- [OSS Torch Connector](https://aliyun.github.io/oss-connector-for-ai-ml/#/torchconnector/introduction) is dedicated to AI training scenarios, including loading [datasets](https://pytorch.org/docs/stable/data.html#dataset-types) from OSS and loading/saving checkpoints from/to OSS.

- [OSS Model Connector](https://aliyun.github.io/oss-connector-for-ai-ml/#/modelconnector/introduction) focuses on AI inference scenarios, loading large model files from OSS into local AI inference frameworks.

The core component of the OSS Connector for AI/ML is implemented in C++ using [PhotonLibOS](https://github.com/alibaba/PhotonLibOS) and is provided as dynamic link libraries within wheel packages. This repository only contains the code of Python.

For details, please refer to [ossconnector.github.io](https://ossconnector.github.io/) or [aliyun.github.io/oss-connector-for-ai-ml](https://aliyun.github.io/oss-connector-for-ai-ml).


## Related

[OSS Connector for AI/ML 中文文档](https://help.aliyun.com/zh/oss/developer-reference/oss-connector-for-al-ml)

## License

This project is licensed under the terms of the [MIT License](LICENSE).
