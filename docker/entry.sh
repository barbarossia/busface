#!/bin/bash
PYTHON=python3
# check if crontab.txt exists
cd /app
echo `pwd`

# ${PYTHON} -m bustag.app.index
${PYTHON} -m busface.sample