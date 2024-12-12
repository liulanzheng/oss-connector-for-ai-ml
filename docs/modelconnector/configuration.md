# Configuration

## Credential

When initializing the OssModelConnector, it is necessary to specify the authentication information required to access OSS.

Two methods are supported: Crendentials provider and Crendentials file.

### Crendentials Provider

OssModelConnector supports all authentication configuration methods of the OSS Python SDK.
Please refer to the documentation:
[How to configure access credentials for OSS SDK for Python](https://www.alibabacloud.com/help/en/oss/developer-reference/python-configuration-access-credentials) /
[如何为OSS Python SDK配置访问凭证](https://help.aliyun.com/zh/oss/developer-reference/python-configuration-access-credentials)

When using it, simply pass the `credentials_provider` to the constructor of the OssModelConnector.

The following is an example of configuring authentication from environment variables.

```bash
export OSS_ACCESS_KEY_ID=<ALIBABA_CLOUD_ACCESS_KEY_ID>
export OSS_ACCESS_KEY_SECRET=<ALIBABA_CLOUD_ACCESS_KEY_SECRET>
export OSS_SESSION_TOKEN=<ALIBABA_CLOUD_SECURITY_TOKEN>
```

```python
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from ossmodelconnector import OssModelConnector

connector = OssModelConnector(endpoint=ENDPOINT,
                              cred_provider=EnvironmentVariableCredentialsProvider(),
                              config_path=CONFIG_PATH)
```

The following is an example of user-custom credentials.

```python
from oss2 import CredentialsProvider
from oss2.credentials import Credentials
from ossmodelconnector import OssModelConnector

class CredentialProviderWrapper(CredentialsProvider):
    def get_credentials(self):
        return Credentials('<access_key_id>', '<access_key_secrect>')


credentials_provider = CredentialProviderWrapper()
connector = OssModelConnector(endpoint=ENDPOINT,
                              cred_provider=credentials_provider,
                              config_path=CONFIG_PATH)
```


### Crendentials File

For now only JSON format credential file is supported.

```bash
mkdir -p /root/.alibabacloud/
cat <<-EOF | tee /root/.alibabacloud/credentials
{
    "AccessKeyId": "<Access-key-id>",
    "AccessKeySecret": "<Access-key-secret>",
    "SecurityToken": "<Security-Token>",
    "Expiration": "2024-08-02T15:04:05Z"
}
EOF
```
`SecurityToken` and  `Expiration` are optional.
The credential file must be updated before expiration to avoid authorization errors.

```python
from ossmodelconnector import OssModelConnector

connector = OssModelConnector(endpoint=ENDPOINT,
                              cred_path='/root/.alibabacloud/credentials',
                              config_path='/tmp/config.json')
```


## Config

The configuration file is responsible for setting parameters such as logging and concurrency. Below is an example.

```bash
mkdir -p /etc/oss-connector/
cat <<-EOF | tee /etc/oss-connector/config.json
{
    "logLevel": 1,
    "logPath": "/var/log/oss-connector/connector.log",
    "auditPath": "/var/log/oss-connector/audit.log",
    "prefetch": {
        "vcpus": 24,
        "workers": 32
    }
    "fastList": {
        "vcpus": 2,
        "workers": 16
    }
}
EOF
```

Pass the path to `config_path` when initializing OssModelConnector.

```python
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from ossmodelconnector import OssModelConnector

connector = OssModelConnector(endpoint=ENDPOINT,
                              cred_provider=EnvironmentVariableCredentialsProvider(),
                              config_path='/etc/oss-connector/config.json')
```

Below is an explanation of each configuration item.

| Field         | Description                                                                                           |
|---------------|-------------------------------------------------------------------------------------------------------|
| logLevel      | The log level for log file, 0 - DEBUG, 1 - INFO, 2 - WARN, 3 - ERROR, 1 is the default value.         |
| logPath       | The path for log file, `/var/log/oss-connector/connector.log` is the default value.                   |
| auditPath     | The path for audit file, `/var/log/oss-connector/audit.log` is the default value.                     |
| prefetch.vcpus    | The vcpu number for perfetching data. 16 is the default value.                                    |
| prefetch.workers  | The worker number for perfetching data in each vcpu. 16 is the default value.                     |
| fastList.vcpus    | The vcpu number for doing fast list. 1 is the default value.                                      |
| fastList.workers  | The worker number for doing fast list in each vcpu. 16 is the default value.                      |