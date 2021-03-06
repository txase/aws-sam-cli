"""
CLI command for "local start-lambda" command
"""

import logging
import click

from samcli.cli.main import pass_context, common_options as cli_framework_options
from samcli.commands.local.cli_common.options import invoke_common_options, service_common_options
from samcli.commands.local.cli_common.invoke_context import InvokeContext
from samcli.commands.local.cli_common.user_exceptions import UserException
from samcli.commands.local.lib.local_lambda_service import LocalLambdaService
from samcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)

HELP_TEXT = """
You can use this command to programmatically invoke your Lambda function locally using the AWS CLI or SDKs.
This command starts a local endpoint that emulates the AWS Lambda service, and you can run your automated
tests against this local Lambda endpoint. When you send an invoke to this endpoint using the AWS CLI or
SDK, it will locally execute the Lambda function specified in the request.\n
\b
SETUP
------
Start the local Lambda endpoint by running this command in the directory that contains your AWS SAM template.
$ sam local start-lambda\n
\b
USING AWS CLI
-------------
Then, you can invoke your Lambda function locally using the AWS CLI
$ aws lambda invoke --function-name "HelloWorldFunction" --endpoint-url "http://127.0.0.1:3001" --no-verify-ssl out.txt
\n
\b
USING AWS SDK
-------------
You can also use the AWS SDK in your automated tests to invoke your functions programatically.
Here is a Python example:
    self.lambda_client = boto3.client('lambda',
                                  endpoint_url="http://127.0.0.1:3001",
                                  use_ssl=False,
                                  verify=False,
                                  config=Config(signature_version=UNSIGNED,
                                                read_timeout=0,
                                                retries={'max_attempts': 0}))
    self.lambda_client.invoke(FunctionName="HelloWorldFunction")
"""


@click.command("start-lambda",
               help=HELP_TEXT,
               short_help="Starts a local endpoint you can use to invoke your local Lambda functions.")
@service_common_options(3001)
@invoke_common_options
@cli_framework_options
@pass_context
def cli(ctx,
        # start-lambda Specific Options
        host, port,

        # Common Options for Lambda Invoke
        template, env_vars, debug_port, debug_args, docker_volume_basedir,
        docker_network, log_file, skip_pull_image, profile
        ):
    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(ctx, host, port, template, env_vars, debug_port, debug_args, docker_volume_basedir,
           docker_network, log_file, skip_pull_image, profile)  # pragma: no cover


def do_cli(ctx, host, port, template, env_vars, debug_port, debug_args,  # pylint: disable=R0914
           docker_volume_basedir, docker_network, log_file, skip_pull_image, profile):
    """
    Implementation of the ``cli`` method, just separated out for unit testing purposes
    """

    LOG.debug("local start_lambda command is called")

    # Pass all inputs to setup necessary context to invoke function locally.
    # Handler exception raised by the processor for invalid args and print errors

    try:
        with InvokeContext(template_file=template,
                           function_identifier=None,  # Don't scope to one particular function
                           env_vars_file=env_vars,
                           debug_port=debug_port,
                           debug_args=debug_args,
                           docker_volume_basedir=docker_volume_basedir,
                           docker_network=docker_network,
                           log_file=log_file,
                           skip_pull_image=skip_pull_image,
                           aws_profile=profile) as invoke_context:

            service = LocalLambdaService(lambda_invoke_context=invoke_context,
                                         port=port,
                                         host=host)
            service.start()

    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))
