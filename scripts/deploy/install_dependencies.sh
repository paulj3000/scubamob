#!/bin/bash
cd ../../ && 
    python3 -m venv env && 
    source env/bin/activate &&
    pip install --upgrade pip &&
    pip install -r requirements.txt
