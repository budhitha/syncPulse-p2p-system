import logging


def read_file_names(file_path):
    """
    Reads a list of file names from a given file.

    Args:
        file_path (str): The path to the file containing the list of file names.

    Returns:
        list: A list of file names (str) read from the file. Returns an empty list if the file is not found.

    Exceptions:
        FileNotFoundError: Logs an error and returns an empty list if the specified file does not exist.
    """
    try:
        with open(file_path, 'r') as file:
            file_names = [line.strip() for line in file.readlines()]
        return file_names
    except FileNotFoundError:
        logging.error(f"Error: File '{file_path}' not found.")
        return []
    except PermissionError:
        logging.error(f"Error: Permission denied for file '{file_path}'.")
        return []
    except UnicodeDecodeError:
        logging.error(f"Error: Cannot decode contents of file '{file_path}'.")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading file '{file_path}': {e}")