import crypt
import os
import string
try:  # 3.6 or above
    from secrets import choice as randchoice
except ImportError:
    from random import SystemRandom
    randchoice = SystemRandom().choice


def generate_random_salt():
    """
    Generate a cryptographically secure random salt for password hashing.

    Returns
    -------
    salt : str
        A hexadecimal string representing the generated random salt.

    Notes
    -----
    This function uses the os.urandom() function to generate a random salt
    with 16 bytes of entropy, which is then converted to a hexadecimal string.
    The generated salt is suitable for use in password hashing algorithms to
    enhance security and prevent rainbow table attacks.
    """
    # Generate a random 16-byte salt
    salt = os.urandom(16)
    # Convert the salt to hexadecimal representation
    salt_hex = salt.hex()
    return salt_hex


def cloud_init_sha512_crypt(password: str, salt: str = None, rounds: int = None):
    """
    Generate a SHA-512 crypt hash suitable for cloud-init configuration.

    Parameters
    ----------
    password : str
        The password to be hashed.
    salt : str, optional
        The salt value to use in the hash (default is None, a random salt will be generated).
    rounds : int, optional
        The number of rounds for hashing (default is None, using a default of 5000 rounds).
        Rounds must be within the range 1000 to 999999999.

    Returns
    -------
    str
        The SHA-512 crypt hash of the password.

    Notes
    -----
    This function generates a SHA-512 crypt hash suitable for cloud-init configuration.
    If `salt` is not provided, a random 8-character salt is generated. The `rounds` parameter
    determines the number of hashing rounds; if not provided, a default of 5000 rounds is used.
    The resulting hash is returned as a string.
    """
    # Adapted from code by Martijn Pieters on Stack Overflow
    # Original source: https://stackoverflow.com/questions/34463134/sha-512-crypt-output-written-with-python-code-is-different-from-mkpasswd
    if salt is None:
        salt = ''.join([
            randchoice(string.ascii_letters + string.digits)
            for _ in range(8)
        ])
    prefix = '$6$'
    if rounds is not None:
        rounds = max(1000, min(999999999, rounds or 5000))
        prefix += f'rounds={rounds}$'
    return str(crypt.crypt(password, prefix + salt))
