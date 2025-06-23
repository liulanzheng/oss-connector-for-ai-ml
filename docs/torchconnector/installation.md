# Installation

## Requirements

- OS: Linux x86-64
- glibc: >= 2.17
- Python: 3.8 - 3.12
- PyTorch:
    - `>= 2.0` (v1.0.0rc1-v1.1.0)
    - `>= 2.3` (since v1.2.0rc1)
- Kernel module: userfaultfd (for checkpoint)

## Install

### Install stable version

```bash
pip install osstorchconnector
```

### Install lastest version

Download the latest osstorchconnector package from [Release](https://github.com/aliyun/oss-connector-for-ai-ml/releases) and use pip to install it.

For example, download the `osstorchconnector/v1.1.0rc1` for Python 3.11 and install:

```bash
wget https://github.com/aliyun/oss-connector-for-ai-ml/releases/download/osstorchconnector%2Fv1.1.0rc1/osstorchconnector-1.1.0rc1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

pip install osstorchconnector-1.1.0rc1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

### Additional configuration for Docker

To use checkpoint-related features within Docker, the container must be run with `--privilege`. This is due to our reliance on userfaultfd to accelerate the reading of checkpoints.