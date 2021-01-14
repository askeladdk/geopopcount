#!/usr/bin/env bash
docker run -d -p 5000:80 -t --name geopopcountd --rm geopopcountd
if [ `uname` = "Darwin" ]; then
    echo "Browser will automatically launch after 8 seconds..."
    sleep 8
    open "http://localhost:5000/api/v1/popcount?place=mumbai&radius=30000"
else
    echo "Browse to..."
    echo "http://localhost:5000/api/v1/popcount?place=mumbai&radius=30000"
fi
