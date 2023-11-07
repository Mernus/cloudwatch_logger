from cloudwatch_logger.runner import DockerCommandRunner

from cloudwatch_logger.tests.mocks import patch_runner__parse_args__get_from_env


@patch_runner__parse_args__get_from_env
def test_runner() -> None:
    runner = DockerCommandRunner()
    runner.run()