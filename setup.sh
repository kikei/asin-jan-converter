#!/bin/bash

EXAMPLE=.env.example
DOTENV=.env

help() {
    cat <<EOF
You can copy file $EXAMPLE as a template and edit it:

    cp $EXAMPLE $DOTENV
    vi $DOTENV

EOF
}

ensure_env() {
    name=$1
    if [ -z ${!name} ]; then
        echo "A variable \"$name\" is required to be declared in $DOTENV."
        help
        exit 1
    fi
}

# Check .env setting
. $DOTENV
if [ $? != 0 ]; then
    echo "Failed to load source $DOTENV."
    help
    exit 1
fi
for name in $(grep = $EXAMPLE | cut -d= -f1); do
    ensure_env $name
done

# Make requirements.txt available from docker script.
cp requirements.txt webapp

# Ensure directory
mkdir -p data/mongodb
mkdir -p data/webapp
