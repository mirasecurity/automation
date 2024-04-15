# Documentation

Assuming you are working inside of the docs directory

## Getting started

Install the required packages:

    pip install -r requirements.txt

## Update Docs

To make changes and update the documentation based on if code changed or the doc files changed use:

    make clean
    sphinx-build -b html source build

To view the changes on unix based systems

    open build/index.html
