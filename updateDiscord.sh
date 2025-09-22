#!/bin/bash

# This script downloads, installs, and updates Discord on Linux.  
# It fetches the latest stable release tarball, removes any existing  
# installation, extracts the new version into the specified directory,  
# and cleans up the downloaded archive.  

DISCORD_URL="https://discord.com/api/download/stable?platform=linux&format=tar.gz"
DOWNLOAD_FILE="discord.tar.gz"
INSTALL_DIR="/PATH/TO/DISCORD/"     # Path to the directory where the Discord directory is located

echo "Start installation from discord from $DISCORD_URL"

# Step 1: Download the tarball
echo "Downloading Discord..."
curl -L "$DISCORD_URL" -o "$DOWNLOAD_FILE"

# Step 2: Remove existing Discord directory
if [ -d "$INSTALL_DIR/Discord" ]; then
    echo "Removing old Discord installation..."
    rm -rf "$INSTALL_DIR/Discord"
fi

# Step 3: Extract new version
echo "Extracting Discord to $INSTALL_DIR"
tar -xzf "$DOWNLOAD_FILE" -C "$INSTALL_DIR"

# Step 4: Clean up
echo "Cleaning up..."
rm "$DOWNLOAD_FILE"

echo "Discord has been updated and installed to $INSTALL_DIR."
