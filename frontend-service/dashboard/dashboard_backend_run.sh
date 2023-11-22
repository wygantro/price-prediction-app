#!/bin/bash

python dashboard_backend_loop.py &
python websocket_conn.py &

wait