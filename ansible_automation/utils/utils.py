import logging as log


def setup_logging(filename: str, log_level: str):
    """
    Set up logging configuration.

    Parameters
    ----------
    filename : str
        The name of the file to which logs will be written.
    log_level : str
        The desired logging level, one of {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}.

    Returns
    -------
    None

    Notes
    -----
    The function configures the logging module to write logs to the specified file with the given level.
    If the provided log level is not recognized, it defaults to 'INFO'.
    """
    # Define log level mapping
    level_mapping = {
        'DEBUG': log.DEBUG,
        'INFO': log.INFO,
        'WARNING': log.WARNING,
        'ERROR': log.ERROR,
        'CRITICAL': log.CRITICAL,
    }

    # Get the log level
    level = level_mapping.get(log_level.upper(), log.INFO)

    # Set up the formatter
    formatter = log.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up logging to file
    file_handler = log.FileHandler(filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    log.getLogger().addHandler(file_handler)

    # Set up logging to console
    console_handler = log.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    log.getLogger().addHandler(console_handler)

    # Set the overall logging level
    log.getLogger().setLevel(level)


class colors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
