import subprocess, sys, time

import datetime as dt 

from classes.zoomActivity import ZoomActivity 
from helpers import clients,logging

logger = logging.set_logging('zoom_activity_monitor')
config = clients.config()

if __name__ == '__main__':
    # set up Kafka Producer for ZoomActivity
    producer = clients.producer(clients.zoom_activity_serializer(), 'kafka-mac')

    # hard-coded command to check current zoom activity on MacOS.
    cmd = 'lsof -i 4UDP | grep zoom | awk \'END{print NR}\''

    # current status
    current_status = None

    # start ZoomActivity capture loop
    try:
        while True:
            # capture ts for record
            ts = int(dt.datetime.now(dt.UTC).strftime('%s'))

            # parse output of command
            p = int(subprocess.getoutput([cmd]))
            
            # extract event from the log line
            if p > 0:
                status = 'IN MEETING'
            else: 
                status = 'OFF MEETING'

            # only want to capute status changes
            if status is not current_status:
                za = ZoomActivity(ts, status)

                # produce zoom activity event
                logger.info(f"Publishing message: {za}")
                producer.produce(config['topics']['zoom'], key='zoom.us', value=za, timestamp=za.zoom_ts * 1000)
                producer.flush()

                current_status = status
            
            time.sleep(5)
    finally:
        producer.flush()
