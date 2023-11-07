# CloudWatch Logger

CloudWatch Logger runs docker container from image, run there some bash command and send logs to AWS CloudWatch.

## Installation
Before installation you need to install poetry and optionally make.

### With make

```bash
git clone git@github.com:Mernus/cloudwatch_logger.git
make install
cp .env.example .env
```

### Without make

```bash
git clone git@github.com:Mernus/cloudwatch_logger.git
poetry install
cp .env.example .env
```

## Tests
To run tests run folowwing code. Before run tests you should insert test data to .env

### With make

```bash
make test
```

### Without make

```bash
poetry install --with dev
docker pull python
cd tests/
poetry run pytest .
```

## Linter
In package included ruff linter. To run linter run folowwing code.

```bash
make check
```

### Without make

```bash
poetry install --with dev
poetry run ruff check . --config ruff.toml
```

## Usage
To view usage of logger run following commands:

```bash
make help
or
poetry run python main.py -h
```

```console
usage: run_bash_in_docker [-h] [--docker-image [DOCKER_IMAGE_NAME]] --bash-command [COMMAND] --aws-cloudwatch-group [CLOUDWATCH_GROUP] --aws-cloudwatch-stream [CLOUDWATCH_STREAM] --aws-access-key-id
                          [ACCESS_KEY] --aws-secret-access-key [SECRET_KEY] --aws-region [REGION]

Run bash command in docker container

options:
  -h, --help            show this help message and exit
  --docker-image [DOCKER_IMAGE_NAME]
                        Docker image used to create container (default: python)
  --bash-command [COMMAND]
                        Bash command to run in container (default: None)
  --aws-cloudwatch-group [CLOUDWATCH_GROUP]
                        Name of an AWS CloudWatch group (default: None)
  --aws-cloudwatch-stream [CLOUDWATCH_STREAM]
                        Name of an AWS CloudWatch stream (default: None)
  --aws-access-key-id [ACCESS_KEY]
                        AWS Access Key (default: None)
  --aws-secret-access-key [SECRET_KEY]
                        AWS Secret Key (default: None)
  --aws-region [REGION]
                        AWS Region (default: None)
```
