#!/bin/bash

# FILE_LOG="$SKP_SHOME/logs/nginx-skp.log"
# mkdir -p $SKP_SHOME/logs
# nginx -c $SKP_SHOME/etc/nginx/nginx.conf >> $FILE_LOG 2>&1

nginx -c $SKP_SHOME/etc/nginx/nginx.conf
