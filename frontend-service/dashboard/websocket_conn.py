# websocket_conn.py

import asyncio
from app.app_init import init_logger


async def save_down(logger):
    """
    Connects to polygon.io websocket, authenticates and streams BTC
    pricing data using async IO module and continuously updates pandas
    dataframe.

    Args:
        logger (logging.Logger): Initialized logger object

    Returns: None
    """
    import logging
    import json
    import pandas as pd
    import websockets

    url = "wss://socket.polygon.io/crypto"

    logger.log(logging.INFO, 'entering save_down function')
    # step 1: connect
    async with websockets.connect(url, timeout=10) as websocket:
        logger.log(logging.INFO, 'entering websocket connection loop')
        connection_msg = await websocket.recv()
        data = json.loads(connection_msg)
        try:
            if data[0]['message'] == 'Connected Successfully':
                logger.log(logging.INFO, 'websocket connected successfully')
            else:
                logger.log(logging.WARNING, 'websocket authenticated failed')
                pass
        except:
            print("Task was cancelled!")
        # step 2: authenticate
        payload = {"action": "auth",
                   "params": ""}
        await websocket.send(json.dumps(payload))
        authenticate_msg = await websocket.recv()
        data = json.loads(authenticate_msg)
        if data[0]['message'] == 'authenticated':
            logger.log(logging.INFO, 'websocket authenticated successfully')
        else:
            logger.log(logging.WARNING, 'websocket authenticated failed')
            pass
        logger.log(logging.INFO, 'websocket streaming')

        data_buffer_lst = []
        data_buffer_df = pd.DataFrame(
            columns=['websocket_datetime', 'websocket_price']) #, 'btc_price'])
        while True:
            # step 3: subscribe
            payload = {"action": "subscribe", "params": "XT.X:BTC-USD"}
            await websocket.send(json.dumps(payload))
            msg = await websocket.recv()
            data = json.loads(msg)

            # append to list of dictionaries and save as json
            for i in range(len(data)):
                data_buffer_lst.append(data[i])

            if len(data_buffer_lst) >= 10:
                data_buffer_lst = data_buffer_lst[-10::]

            # append to dataframe and save as csv
            try:
                # convert unix time to datetime object
                websocket_datetime_converted = pd.to_datetime(
                    data_buffer_lst[-1]['t'], unit='ms')

                add_row = {'websocket_datetime': websocket_datetime_converted,
                           'websocket_price': data_buffer_lst[-1]['p'],
                           'btc_price': data_buffer_lst[-1]['p']}
                data_buffer_df = pd.concat(
                    [data_buffer_df, pd.DataFrame([add_row])], ignore_index=True)
            except:
                pass

            # slice dataframe greater than length 10 rows
            if len(data_buffer_df) >= 40:
                data_buffer_df = data_buffer_df.tail(40)

            # save data_buffer_df
            file_path = './dataframes/data_buffer_df.csv'
            data_buffer_df.to_csv(file_path, index=False)


# run async function
logger = init_logger('frontend-service')
asyncio.run(save_down(logger))