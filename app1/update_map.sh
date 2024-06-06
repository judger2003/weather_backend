#!/bin/bash
source /root/anaconda3/etc/profile.d/conda.sh
conda activate weather
python home/appfile/backend/djangoProject/app1/get_api.py
echo "Ran get_api.py at $(date)" >> /home/appfile/backend/djangoProject/app1/get_api.log