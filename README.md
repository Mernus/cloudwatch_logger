# CloudWatch Logger

CloudWatch Logger runs docker container from image, run there some bash command and send logs to AWS CloudWatch.

## Installation
Before installation you need to install poetry and optionally make.

### With make

```bash
git clone git@github.com:Mernus/cloudwatch_logger.git
make install
```

### Without make

```bash
git clone git@github.com:Mernus/cloudwatch_logger.git
poetry install
cp .env.example .env
```

# Usage

