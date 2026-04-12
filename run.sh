#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting WeChat Export Tool..."
python wechat_export.py --help
