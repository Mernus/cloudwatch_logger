from abc import ABC, abstractmethod
from time import time
from typing import Any

import boto3

from cloudwatch_logger.consts import MAX_MSG_SIZE, MAX_RETRIES, NULL_SEQUENCE_TOKEN
from cloudwatch_logger.mixins import ConsoleLoggingMixin


class BaseLogger(ABC):
    """Base logger."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log message to logging system.

        Args:
            message (str): Message.
        """
        raise NotImplementedError


class CloudWatchLogger(BaseLogger, ConsoleLoggingMixin):
    """AWS CloudWatch logger.
    
    Attributes:
        __sequence_token (str): Log sequence token.
        cloudwatch_group (str): AWS CloudWatch group name.
        cloudwatch_stream (str): AWS CloudWatch stream name.
        __session (boto3.Session): AWS Session.
        __client (boto3.Client): AWS client.
    """

    def __init__(
        self,
        cloudwatch_group: str,
        cloudwatch_stream: str,
        access_key: str,
        secret_key: str,
        region: str,
    ) -> None:
        """Initialize CloudWatch logger.

        Args:
            cloudwatch_group (str): AWS CloudWatch group name.
            cloudwatch_stream (str): AWS CloudWatch stream name.
            access_key (str): AWS Access key.
            secret_key (str): AWS Secret key.
            region (str): AWS Region.
        """
        super().__init__()

        self.__sequence_token: str | None = None
        self.cloudwatch_group = cloudwatch_group
        self.cloudwatch_stream = cloudwatch_stream

        # Init AWS session
        self.__session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        # Init cloudwatch client
        self.__client = self.__session.client("logs")

        self._ensure_log_group()

    def log(self, message: str) -> None:
        """Log message to CloudWatch.

        Args:
            message (str): Message.
        """

        if message == "":
            self.logger.warning("We don't send empty messages to CloudWatch")
            return

        if len(message) > MAX_MSG_SIZE:
            self.logger.warning("Very long message. Truncating..")
            message = message[:MAX_MSG_SIZE]

        log_entry = dict(
            timestamp=int(time() * 1000),
            message=message,
        )
        log_event_data = dict(
            logGroupName=self.cloudwatch_group,
            logStreamName=self.cloudwatch_stream,
            logEvents=[log_entry]
        )

        if self.__sequence_token is not None:
            log_event_data["sequenceToken"] = self.__sequence_token

        self.logger.info("Delivering logs...")
        for retry in range(MAX_RETRIES):
            try:
                resp = self.__client.put_log_events(**log_event_data)
                break
            except (
                self.__client.exceptions.DataAlreadyAcceptedException,
                self.__client.exceptions.InvalidSequenceTokenException,
            ) as exc:
                self.logger.warning("Event alredy logged or token is not valid")
                # We get last word in message to verify what token is expecting on next request
                next_sequence_token = exc.response["Error"]["Message"].rsplit(" ", 1)[-1]

                if next_sequence_token != NULL_SEQUENCE_TOKEN:
                    log_event_data["sequenceToken"] = next_sequence_token
                else:
                    # If null - no tokens expecting
                    log_event_data.pop("sequenceToken", None)
            except self.__client.exceptions.ResourceNotFoundException:
                self.logger.warning("log strean not found. Creating new...")
                # If log strean not found - create it
                self._create_log_stream()
                log_event_data.pop("sequenceToken", None)
            except Exception as exc:
                self.logger.warning(f"Can`t deliver logs. Retry: #{retry + 1}. Error: \n\n{exc}")
        
        if resp is None or resp.get("rejectedLogEventsInfo", {}):
            self.logger.warning(f"Can`t deliver logs. Invalid response: \n\n{resp}")
        elif "nextSequenceToken" in resp:
            self.__sequence_token = resp["nextSequenceToken"]

    def _ensure_log_group(self) -> None:
        """Return log group if exists. If not - create and return."""
        try:
            paginator = self.__client.get_paginator("describe_log_groups")
            for page in paginator.paginate(logGroupNamePrefix=self.cloudwatch_group):
                for log_group in page.get("logGroups", []):
                    if log_group["logGroupName"] == self.cloudwatch_group:
                        return
        except self.__client.exceptions.ClientError:
            pass

        self._call("create_log_group", logGroupName=self.cloudwatch_group)

    def _create_log_stream(self) -> None:
        """Create log stream in group."""
        self._call(
            "create_log_stream",
            logGroupName=self.cloudwatch_group,
            logStreamName=self.cloudwatch_stream,
        )

    def _call(self, method: str, *args: Any, **kwargs: Any) -> None:
        """Call AWS client resource methods with ignoring existance and abort of operation.

        Args:
            method (str): Client method.
        """
        callable_method = getattr(self.__client, method)

        try:
            callable_method(*args, **kwargs)
        except (
            self.__client.exceptions.OperationAbortedException,
            self.__client.exceptions.ResourceAlreadyExistsException,
        ):
            pass
        except self.__client.exceptions.ClientError:
            self.logger.error("Can`t make request to AWS CloudWatch. Invalid response.\n")
            raise
