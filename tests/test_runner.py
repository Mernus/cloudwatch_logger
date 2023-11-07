from mocks import patch_runner__parse_args__get_from_env

from cloudwatch_logger.runner import DockerCommandRunner


@patch_runner__parse_args__get_from_env
def test_runner() -> None:
    runner = DockerCommandRunner()
    runner.run()