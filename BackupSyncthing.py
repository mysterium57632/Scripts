#!/usr/bin/env python3

# This script automates encrypted backups to HiDrive using the WebDAV API.  
# It encrypts each directory inside the source path with a provided key file,  
# uploads the resulting .zip.enc files to HiDrive, and verifies the upload  
# by comparing remote and local file sizes. If the verification succeeds,  
# the local encrypted copies are removed. The script processes multiple  
# directories in parallel using worker threads, logs all activity with  
# timestamps, and reports any failures at the end.

import requests
import threading
import subprocess
import builtins
import os
import xml.etree.ElementTree as ET

from datetime import datetime
from pathlib import Path
from requests.auth import HTTPBasicAuth

original_print = builtins.print

drive_path = "/home/paull/drive/"                                                       # Path of the source directory to back up     
webdav_url = "https://webdav.hidrive.strato.com/users/HIDRIVE-USERNAME/folder-path/"    # HiDrive destination path
username = "HIDRIVE-USERNAME"                                                           # HiDrive username
password = "HIDRIVE-PASSWORD"                                                           # HiDrive password
path_to_key = "/PATH-TO-ENCRYPTION-KEY-FILE.key"                                        # File used to encrypt the directory before uploading
failure_list = []

def worker(idd, path):
    print(f"Worker-{idd}: starting on {path}")
    process = subprocess.Popen(
        ["python3", "Encrypt.py", path, path_to_key],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output:
            print(f"Worker-{idd}: " + output, end='')
        if error:
            print(f"Worker-{idd}: " + error, end='')
        if not output and not error and process.poll() is not None:
            break
    err = process.poll() != 0
    if err:
        failure_list.append(path)
        print(f"Worker-{idd}: interrupted through errors\n")
        return

    src = path + ".zip.enc"
    err = upload(src, os.path.basename(src), idd) == -1
    if err:
        failure_list.append(path)
    print(f"Worker-{idd}: done {'with' if err else 'without'} errors\n")


def get_remote_size(url):
    headers = {"Depth": "0"}
    body = """<?xml version="1.0"?>
    <d:propfind xmlns:d="DAV:">
      <d:prop>
        <d:getcontentlength/>
      </d:prop>
    </d:propfind>"""

    response = requests.request("PROPFIND", url, data=body, headers=headers, auth=HTTPBasicAuth(username, password))
    if response.status_code not in [207, 200]:
        raise Exception(f"PROPFIND failed: {response.status_code} {response.text}")

    tree = ET.fromstring(response.text)
    ns = {"d": "DAV:"}
    length = tree.find(".//d:getcontentlength", ns)
    return int(length.text) if length is not None else None


def upload(source, filename, idd):
    upload_url = webdav_url + filename
    with open(source, 'rb') as f:
        response = requests.put(upload_url, data=f, auth=HTTPBasicAuth(username, password))

    if response.status_code in [200, 201, 204]:
        local_size = os.path.getsize(source)
        try:
            remote_size = get_remote_size(upload_url)
        except Exception as e:
            print(f"Worker-{idd}: Could not verify remote file size: {e}")
            return -1
        if remote_size == local_size:
            print(f"Worker-{idd}: File {filename} uploaded successfully.")
        else:
            print(f"Worker-{idd}: File {filename} upload Status unknown, failed verifying file size.")
            return -1

        try:
            os.remove(source)
            print(f"Worker-{idd}: Removed local file {source}")
        except OSError as e:
            print(f"Worker-{idd}: Could not remove local file {source}. Error: {e}")
        return 0
    else:
        print(f"Worker-{idd}: Upload failed for {filename}. Status code: {response.status_code}")
        print(f"Worker-{idd}: " + response.text)
        return -1


def print(*args, **kwargs):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    original_print(timestamp, *args, **kwargs)


def printt(*args, **kwargs):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    original_print("\n" + timestamp, *args, **kwargs)


def main():
    directory = Path(drive_path)
    threads = []
    w_id = 0
    for file_path in directory.glob("*"):
        if file_path.exists():
            file = str(file_path.resolve())
            if "lost+found" in file or not file_path.is_dir(): continue
            t = threading.Thread(target=worker, args=(w_id, file))
            t.start()
            threads.append(t)
            w_id += 1
    for t in threads:
        t.join()

    if not failure_list:
        printt("All files got uploaded successfully")
    else:
        printt(f"The following {len(failure_list)} files could not be uploaded:")
        for f in failure_list:
            print(f)


if __name__ == "__main__":
    start =  datetime.now()
    main()
    start = datetime.now() - start
    print(f"Finished after {start}s")
