#!/usr/bin/env python3

# This script zips and/or encrypts files and directories using OpenSSL with AES-256.  
# It supports three modes of operation:  
#   - zip_enc (default): zip the source and then encrypt the zip file  
#   - ozip: only create a zip archive without encryption  
#   - oenc: only encrypt an existing file without zipping  
# The encryption key can be provided directly or read from a key file.  
# Output filenames can be customized, and intermediate zip files can be kept  
# or automatically removed after encryption. The script validates inputs,  
# handles errors gracefully, and exits with appropriate status codes.  

import argparse
import sys
import zipfile
import os
import subprocess

def read_key(key):
    if key is None:
        return None
    if (key.startswith("\"") and key.endswith("\"")) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1]
    if os.path.exists(key):
        with open(key, 'r', encoding='utf-8') as f:
            key = f.read().strip()
            if not key:
                raise ValueError("Key file could not be read or is empty.")
    return key

def zip_file(src, out):
    try:
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(src):
                for root, _, files in os.walk(src):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        arcname = os.path.relpath(abs_path, start=src)
                        zipf.write(abs_path, arcname)
            else:
                arcname = os.path.basename(src)
                zipf.write(src, arcname)
        return 0
    except (OSError, zipfile.BadZipFile) as e:
        print(f"Zipping failed: {e}")
        return -1

def encrypt_with_openssl(src, out, key):
    try:
        subprocess.run([
            "openssl", "enc", "-aes-256-cbc",
            "-salt",
            "-pbkdf2",
            "-in", src,
            "-out", out,
            "-pass", f"pass:{key}"
        ], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"OpenSSL encryption failed: {e}")
        return -1

def main():
    parser = argparse.ArgumentParser(description="Zip and encrypt a file with AES-256 using OpenSSL and a given passphrase")

    parser.add_argument("src", help="source file or directory")
    parser.add_argument("key", help="encryption key or path to key file")

    parser.add_argument("-m", "--mode", choices=["zip_enc", "ozip", "oenc"], default="zip_enc",
                        help="operation mode: default is zip_enc (zip and encrypt), also ozip (only zip) or oenc (only encrypt)")
    parser.add_argument("-o", "--output", help="output file name (default: src.zip.enc)", default=None)
    parser.add_argument("-k", "--keep", action="store_true", default=False,
                        help="keep the zip file after encryption (default: remove it)")

    args = parser.parse_args()

    src = args.src
    custom_out = args.output is not None
    out = src if args.output is None else args.output

    # Ensure the src file or directory exists
    if not os.path.exists(src):
        print(f"Source file or directory '{src}' does not exist.")
        return

    # Ensure that there is a key or key file provided
    key = args.key
    try:
        key = read_key(key)
    except ValueError as e:
        print(e)
        return

    # Zip the file
    if args.mode == "ozip":
        out = out if custom_out else out + ".zip"
        e = zip_file(src, out)
        if e == -1:
            sys.exit(1)
        print(f"Zipped '{src}' to '{out}'")
    elif args.mode == "oenc":
        out = out if custom_out else out + ".enc"
        e = encrypt_with_openssl(src, out, key)
        if e == -1:
            sys.exit(1)
        print(f"Encrypted '{src}' to '{out}'")
    else:
        zip_out = src + ".zip"
        zip_file(src, zip_out)
        if args.keep: print(f"Zipped '{src}' to '{zip_out}'")
        out = out if custom_out else out + ".zip.enc"
        e = encrypt_with_openssl(zip_out, out, key)

        # Check if encryption was successful
        if e == -1:
            if not args.keep:
                os.remove(zip_out)
                print("zip file removed due to encryption failure")
                sys.exit(1)
            return

        print(f"Encrypted '{zip_out if args.keep else src}' to '{out}'")
        if not args.keep:
            os.remove(zip_out)

    # Success
    sys.exit(0)

if __name__ == "__main__":
    main()
