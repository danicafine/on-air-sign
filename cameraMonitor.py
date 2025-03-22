#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
import subprocess, sys, time
import shlex, re

from classes.cameraActivity import CameraActivity 
from helpers import clients,logging

logger = logging.set_logging('camera_activity_monitor')
config = clients.config()


# extracts camera activity events from input logs.
# ignores lines that aren't relevant.
def extract_camera_activity(log_line):
    try:
        # line contain items we KNOW aren't camera activity
        # then return empty string
        if "Filtering" in log_line or "Timestamp" in log_line:
            return None

        # extract UTC timestamp
        # of the form 2025-03-17 07:05:10.067555-0700
        date_time = log_line[:19] + log_line[26:31]
        pattern = '%Y-%m-%d %H:%M:%S%z'
        ts = int(time.mktime(time.strptime(date_time, pattern)))

        # extract status
        if "AVCaptureSessionDidStartRunningNotification" in log_line:
            status = "START"
        elif "AVCaptureSessionDidStopRunningNotification" in log_line:
            status = "STOP"
        else:
            # not a valid log line
            return None

        # extract application using regex (?:\s+\d{1}\s+)([^:]+)
        application = re.search(r"(?:\s+\d{1}\s+)([^:]+)", log_line).group(1)
    
        # build camera activity object
        ca = CameraActivity(ts, status, application)
        return ca

    except Exception as e:
        logger.error("Got exception %s", e)


if __name__ == '__main__':
    # set up Kafka Producer for CameraActivity
    producer = clients.producer(clients.camera_activity_serializer(), 'kafka-mac')

    # hard-coded command to capture camera activity on MacOS.
    cmd = 'log stream --predicate \'(eventMessage CONTAINS \"AVCaptureSessionDidStartRunningNotification\" || eventMessage CONTAINS \"AVCaptureSessionDidStopRunningNotification\")\''

    # parse command and set up subprocess to monitor the stdout.
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # start CameraActivity capture loop
    for line in iter(p.stdout.readline, ''):
        try:
            sys.stdout.flush()
            
            # extract event from the log line
            ca = extract_camera_activity(line)

            if ca is not None:
                # produce camera activity event
                logger.info(f"Publishing message: key, value: ({ca.application_id},{ca})")
                producer.produce(config['topics']['camera'], key=ca.application_id, value=ca, timestamp=ca.camera_ts * 1000) 
        finally:
            producer.flush()
