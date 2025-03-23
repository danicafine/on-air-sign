import time

#from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from confluent_kafka.error import SerializationError

from helpers import clients,logging

config = clients.config('./config/config.yaml')
logger = logging.set_logging('on_air_sign', config['pi']['logging.directory'])


# consumes from the camera activity topic
# returns true if the light needs to be on
def get_c_status(c_consumer, c_on):
    try:
        msg = c_consumer.poll(1.0)

        if msg is not None:
            # received good record, check status
            return msg.value().camera_status == 'START'
            
        return c_on
    except SerializationError as e:
        # report malformed record, return current light state
        logger.error("Message deserialization failed %s", e)
        return c_on


# consumes from the zoom activity topic
# returns true if the light needs to be on
def get_z_status(z_consumer, z_on):
    try:
        msg = z_consumer.poll(1.0)

        if msg is not None:
            # received good record, check status
            return msg.value().zoom_status == 'IN MEETING'
            
        return z_on
    except SerializationError as e:
        # report malformed record, return current light state
        logger.error("Message deserialization failed %s", e)
        return is_on


if __name__ == '__main__':
    # set up Kafka Consumer for CameraActivity
    c_consumer = clients.consumer(clients.camera_activity_deserializer(config), config['pi']['kafka'], 'on-air-sign-consumer', [config['topics']['camera']])

    # set up Kafka Consumer for CameraActivity
    z_consumer = clients.consumer(clients.zoom_activity_deserializer(config), config['pi']['kafka'], 'on-air-sign-consumer', [config['topics']['zoom']])

    # on air sign options
    options = RGBMatrixOptions()
	options.rows=64
	options.cols=64
	options.hardware_mapping='adafruit-hat'
	matrix = RGBMatrix(options=options)

	font = graphics.Font()
	font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/9x18.bdf")
	textColor = graphics.Color(0,0,255)

	canvas = matrix.CreateFrameCanvas()

    c_on = False
    z_on = False

    # start readings capture loop
    try:
        while True:
            # fetch latest camera status
            c_on = get_c_status(c_consumer, c_on)

            # fetch latest zoom status
            z_on = get_z_status(z_consumer, z_on)

            print(f"Status: {c_on or z_on}")

            # update on air sign
            if c_on or z_on:
	            canvas.Clear()
				graphics.DrawText(canvas, font, 23, 25, textColor, 'ON')
				graphics.DrawText(canvas, font, 18, 45, textColor, 'AIR')
			else:
				#canvas.Clear()

            time.sleep(1)
    except Exception as e:
        	logger.error("Got exception %s", e)
    finally:
        canvas.Clear()
