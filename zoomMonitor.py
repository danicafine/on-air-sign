#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
import subprocess, sys, time

import datetime as dt 

from classes.zoomActivity import ZoomActivity 
from helpers import clients,logging


config = clients.config('./config/config.yaml')
logger = logging.set_logging('zoom_activity_monitor', config['mac']['logging.directory'])

if __name__ == '__main__':
    # set up Kafka Producer for ZoomActivity
    producer = clients.producer(clients.zoom_activity_serializer(config), config['mac']['kafka'])

    # hard-coded command to check current zoom activity on MacOS.
    cmd = 'lsof -i 4UDP | grep zoom | awk \'END{print NR}\''

    # current status
    current_status = None

    # start ZoomActivity capture loop
    try:
        while True:
            # capture ts for record
            ts = int(dt.datetime.now().strftime('%s'))

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
                logger.info(f"Publishing message: key, value: (workmac,{za})")
                producer.produce(config['topics']['zoom'], key='workmac', value=za, timestamp=za.zoom_ts * 1000)
                producer.flush()

                current_status = status
            
            time.sleep(1)
    finally:
        producer.flush()
