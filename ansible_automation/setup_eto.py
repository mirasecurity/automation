import argparse
import time

import urllib3
from bravado.client import SwaggerClient
from bravado.client import SwaggerFormat
from bravado.requests_client import RequestsClient


def connect(server_url, username=None, password=None, new_password=None, ssl_verify=True):
    """
    Connect to a server and return a SwaggerClient instance.

    Parameters
    ----------
    server_url : str
        The URL of the server to connect to.
    username : str, optional
        The username for authentication (default is None).
    password : str, optional
        The password for authentication (default is None).
    new_password : str, optional
        The new password to set (default is None).
    ssl_verify : bool, optional
        Whether to verify SSL certificates (default is True).

    Returns
    -------
    swagger_client : SwaggerClient
        A SwaggerClient instance connected to the specified server.

    Notes
    -----
    This function connects to a server using the provided `server_url`. If `ssl_verify` is set to False,
    SSL certificate verification is disabled. The function initializes a SwaggerClient instance with
    customized configurations and returns it. If `username` and `password` are provided, authentication
    is performed using the provided credentials. If `new_password` is provided, it is used for changing
    the password. The resulting SwaggerClient instance is returned.
    """
    if not ssl_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    http_client = RequestsClient(ssl_verify=ssl_verify)
    swagger_client = SwaggerClient.from_url(
        '%s/swagger.json' % server_url,
        http_client=http_client,
        config={
            'validate_responses': False,
            'validate_requests': True,
            'validate_swagger_spec': False,
            'use_models': False,
            'formats': [
                SwaggerFormat(
                    format='uri',
                    to_wire=lambda b: b if isinstance(b, str) else str(b),
                    to_python=lambda s: s if isinstance(s, str) else str(s),
                    validate=lambda v: v,
                    description='Converts [wire]string:byte <=> python byte',
                ),
                SwaggerFormat(
                    format='email',
                    to_wire=lambda b: b if isinstance(b, str) else str(b),
                    to_python=lambda s: s if isinstance(s, str) else str(s),
                    validate=lambda v: v,
                    description='Converts [wire]string:byte <=> python byte',
                ),
                SwaggerFormat(
                    format='ipv4',
                    to_wire=lambda b: b if isinstance(b, str) else str(b),
                    to_python=lambda s: s if isinstance(s, str) else str(s),
                    validate=lambda v: v,
                    description='Converts [wire]string:byte <=> python byte',
                ),
                SwaggerFormat(
                    format='ipv6',
                    to_wire=lambda b: b if isinstance(b, str) else str(b),
                    to_python=lambda s: s if isinstance(s, str) else str(s),
                    validate=lambda v: v,
                    description='Converts [wire]string:byte <=> python byte',
                ),
            ],
        },
    )
    if username is not None and password is not None:
        swagger_client.auth.auth_login_create(
            data=swagger_client.get_model('Login')(
                username=username, password=password, new_password=new_password,
            ),
        ).response().result
    swagger_client.server_url = server_url
    return swagger_client


def setup_eto_with_retry(hostname, username, old_password, password, allow_enrollment, max_retries=30, retry_delay=5):
    """
    Setup ETO (Encrypted Traffic Orchestrator) and change it's enrollment state to allow.

    Parameters
    ----------
    hostname : str
        The hostname of the server.
    username : str
        The username for authentication.
    old_password : str
        The old password for authentication.
    password : str
        The new password for authentication.
    max_retries : int, optional
        The maximum number of retries in case of failure. Default is 30.
    retry_delay : int, optional
        The delay (in seconds) between retries. Default is 5.

    Raises
    ------
    SystemError
        If the maximum number of retries is reached without success.
    """
    for attempt in range(1, max_retries + 1):
        try:
            try:
                # Changing password from old to new for initial login
                client = connect(
                    f'https://{hostname}/api', username, old_password, password, False,
                )
            except Exception as e:
                print(f'Could not establish a connection {e}')
                time.sleep(retry_delay)
                continue
            # Enable enrollment on the ETO
            if allow_enrollment:
                try:
                    response = client.system.system_enrollment_enroll_update(
                        data={
                            'state': 'allow',
                        },
                    ).response().result
                    print(response)
                except Exception as e:
                    print(f'Could not change enrollment state {e}')
                    time.sleep(retry_delay)
            # If the above steps succeed, break out of the loop
            break
        except Exception as e:
            print(f'Attempt {attempt} failed: {str(e)}')
            if attempt < max_retries:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                print('Max retries reached. Exiting.')
                SystemError('Max retries reached. Exiting.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup ETO')
    parser.add_argument(
        '--ip', required=True,
        help='IPv4 address of the server',
    )
    parser.add_argument(
        '--username', required=True,
        help='Username for authentication',
    )
    parser.add_argument(
        '--old_password', required=True,
        help='Old password for authentication',
    )
    parser.add_argument(
        '--password', required=True,
        help='New password for authentication',
    )
    parser.add_argument(
        '--allow-enrollment', default=True,
        help='Enable enrollment for ETO',
    )
    args = parser.parse_args()

    setup_eto_with_retry(
        args.ip, args.username,
        args.old_password, args.password, args.allow_enrollment,
    )
