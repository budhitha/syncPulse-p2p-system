import os
import random
import hashlib
from flask import Flask, jsonify, send_file

from config.config import FLASK_API_PORT

app = Flask(__name__)

# Directory to store generated files
FILE_DIR = './files'
os.makedirs(FILE_DIR, exist_ok=True)

def generate_file():
    """Generate a random file with size between 2-10 MB and return its details."""
    file_size_mb = random.randint(2, 10)
    file_size_bytes = file_size_mb * 1024 * 1024
    file_name = f"file_{file_size_mb}MB.bin"
    file_path = os.path.join(FILE_DIR, file_name)

    # Write the file in chunks and calculate SHA-256 hash incrementally
    sha256_hash = hashlib.sha256()
    chunk_size = 1024 * 1024  # 1 MB
    bytes_written = 0
    with open(file_path, 'wb') as f:
        while bytes_written < file_size_bytes:
            chunk = os.urandom(min(chunk_size, file_size_bytes - bytes_written))
            f.write(chunk)
            sha256_hash.update(chunk)
            bytes_written += len(chunk)

    sha256_hash = sha256_hash.hexdigest()

    return file_name, file_path, file_size_mb, sha256_hash

@app.route('/generate', methods=['GET'])
def generate_and_get_file():
    """Generate a file and return its details."""
    file_name, file_path, file_size_mb, sha256_hash = generate_file()
    return jsonify({
        'file_name': file_name,
        'file_size_mb': file_size_mb,
        'sha256_hash': sha256_hash
    })

@app.route('/download/<file_name>', methods=['GET'])
def download_file(file_name):
    """Download the generated file."""
    file_path = os.path.join(FILE_DIR, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_API_PORT, debug=True)