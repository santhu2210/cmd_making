#! /bin/bash

readonly sourceFile="./envr/bin/activate"

source ${sourceFile}
# virtualenv is now active.

nohup python app.py & > flask_details.log &
# flask server run on background and details writed in log file