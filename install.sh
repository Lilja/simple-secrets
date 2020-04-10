#!/bin/sh

filename="simple_secret.py"

if [ ! -f "$filename" ]; then
    curl https://raw.githubusercontent.com/Lilja/simple-secrets/master/simple_secret.py > $filename

    chmod +x $filename
fi
