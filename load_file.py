import os

def load_file(file_path: str) -> str:
    """
    Load and return the contents of a text-based file.
    
    Args:
        file_path (str): Absolute path to the file.
    
    Returns:
        str: File contents as a string.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
    """
    if not os.path.isabs(file_path):
        raise ValueError("Please provide an absolute file path.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()