#!/bin/bash
# This script pack source code to the specified destination directory

dest=$1
dest_path="${dest}/resbibman.zip"

if [ $dest ]; then
        if [ -d $dest ]; then
            echo "Pack source to ${dest_path}"
        else
            echo "Destination directory: ${dest} not exists, abort"
            exit
        fi
else
    echo "No destination specified, abort"
    exit
fi

if [ -f $dest_path ]; then
    echo "delete old $dest_path."
    rm $dest_path
fi

echo "Packing..."
zip -qr ${dest_path} $(git ls-files)
echo "Done."
