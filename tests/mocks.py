import os
from typing import Callable
from unittest.mock import patch

import argparse

parse_args = "argparse.ArgumentParser.parse_args"


def parse_args_mock_generator() -> Callable:

    def parse_args_inner(self: argparse.ArgumentParser) -> argparse.Namespace:
        return argparse.Namespace(
            docker_image=os.getenv("DOCKER_IMAGE"),
            bash_command=os.getenv("BASH_COMMAND"),
            aws_cloudwatch_group=os.getenv("AWS_CLOUDWATCH_GROUP"),
            aws_cloudwatch_stream=os.getenv("AWS_CLOUDWATCH_STREAM"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION"),
        )

    return parse_args_inner


patch_runner__parse_args__get_from_env = patch(
    parse_args,
    parse_args_mock_generator(),
)
