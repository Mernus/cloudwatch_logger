import logging
from abc import ABC, abstractmethod
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
)

import docker

from logger import CloudWatchLogger


class BaseCommandRunner(ABC):
    """Base command runner."""

    @abstractmethod
    def run(self) -> None:
        """Run command."""
        raise NotImplementedError

class DockerCommandRunner(BaseCommandRunner):
    """Docker command runner.
    Run bash command inside docker and stream logs from it to AWS CloudWatch.

    Attributes:
        parser (ArgumentParser): Arguments parser.
        docker (Client): Docker client.
    """

    def __init__(self) -> None:
        self.parser = self._init_parser()
        self.docker = docker.from_env()

    def _init_parser(self) -> ArgumentParser:
        """Init argument parser with arguments passed.

        Returns:
            ArgumentParser: Arguments parser.
        """
        parser = ArgumentParser(
            prog="run_bash_in_docker",
            description="Run bash command in docker container",
            formatter_class=ArgumentDefaultsHelpFormatter,
            allow_abbrev=False,
        )
        parser.add_argument(
            "--docker-image",
            type=str,
            help="Docker image used to create container",
            nargs="?",
            default="python",
            metavar="DOCKER_IMAGE_NAME",
        )
        parser.add_argument(
            "--bash-command",
            type=str,
            help="Bash command to run in container",
            nargs=1,
            required=True,
            metavar="COMMAND",
        )
        parser.add_argument(
            "--aws-cloudwatch-group",
            type=str,
            help="Name of an AWS CloudWatch group",
            nargs=1,
            required=True,
            metavar="CLOUDWATCH_GROUP",
            # add validators
        )
        parser.add_argument(
            "--aws-cloudwatch-stream",
            type=str,
            help="Name of an AWS CloudWatch stream",
            nargs=1,
            required=True,
            metavar="CLOUDWATCH_STREAM",
        )
        parser.add_argument(
            "--aws-access-key-id",
            type=str,
            help="AWS Access Key",
            nargs=1,
            required=True,
            metavar="ACCESS_KEY",
        )
        parser.add_argument(
            "--aws-secret-access-key",
            type=str,
            help="AWS Secret Key",
            nargs=1,
            required=True,
            metavar="SECRET_KEY",
        )
        parser.add_argument(
            "--aws-region",
            type=str,
            help="AWS Region",
            nargs=1,
            required=True,
            metavar="REGION",
        )
        return parser

    def run(self) -> None:
        """Run command with parsed data."""
        args = self.parser.parse_args()
        
        try:
            self.docker.images.get(args.docker_image)
        except docker.errors.ImageNotFound:
            logging.error("No such docker image")
            exit()
        except docker.errors.APIError:
            logging.error("Errors with docker server. Try again later.")
            exit()

        logging.info("Docker image exist")
        try:
            logging.info("Running docker container")
            container = self.docker.containers.run(
                image=args.docker_image,
                command=f"bash -c '{args.bash_command}'",
                remove=True,
                detach=True,
            )
            logging.info("Container is up")

            logging.info("Running cloudwatch logger")
            logger = CloudWatchLogger(
                cloudwatch_group=args.aws_cloudwatch_group,
                cloudwatch_stream=args.aws_cloudwatch_stream,
                access_key=args.aws_access_key_id,
                secret_key=args.aws_secret_access_key,
                region=args.aws_region,
            )
            logging.info("Logger is up")

            logging.info("Streaming docker logs")
            for line in container.logs(stream=True):
                logger.log(line.decode("utf-8"))

        except docker.errors.DockerException as exc:
            logging.error(f"Errors with docker. Info: {exc}")

        finally:
            logging.info("Shutting down")
            if container is not None:
                container.remove(force=True)
        