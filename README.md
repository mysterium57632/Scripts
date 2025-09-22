# Backup & Utility Scripts

This repository contains a set of small scripts I use to automate backups and keep Discord updated on my Linux system.  

---

## 1. `backup_to_hidrive.py`
This script automates encrypted backups to HiDrive using the WebDAV API.  
It encrypts each directory from a given source path, uploads the result to HiDrive, verifies the upload by comparing file sizes, and removes the local encrypted files after success. Multiple directories are processed in parallel, and all actions are logged with timestamps.  

I use this as part of my nightly **Syncthing backup chain**, so my synced data is automatically encrypted and pushed to HiDrive every night.  

---

## 2. `Encrypt.py`
A helper script for the backup process.  
It can zip and/or encrypt files or directories using **OpenSSL AES-256**. It supports three modes:  
- `zip_enc` (default): zip and then encrypt  
- `ozip`: only zip  
- `oenc`: only encrypt  

The encryption key can be provided directly or stored in a file. It’s used by the backup script but can also be run standalone.  

---

## 3. `update_discord.sh`
A Bash script to download and update Discord on Linux.  
It fetches the latest stable release tarball, removes any old installation, extracts the new version into the specified directory, and cleans up the downloaded archive.  

Since I don’t use a GUI package manager for Discord on Linux, and updating requires downloading a new tarball each time, I wrote this script to handle the process automatically.  

---

## Notes
- All scripts are written with simplicity and automation in mind.

