#!/bin/bash

python dashboard_backend_loop.py &
python websocket_conn.py &
python websocket_conn_eth.py &

wait