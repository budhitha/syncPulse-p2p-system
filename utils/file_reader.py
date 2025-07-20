import logging


def read_file_names(file_path):
    try:
        with open(file_path, 'r') as file:
            file_names = [line.strip() for line in file.readlines()]
        return file_names
    except FileNotFoundError:
        logging.error(f"Error: File '{file_path}' not found.")
        return []