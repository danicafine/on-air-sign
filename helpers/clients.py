from confluent_kafka import SerializingProducer, DeserializingConsumer
from confluent_kafka.error import SerializationError
from confluent_kafka.serialization import StringSerializer, StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

from classes.cameraActivity import CameraActivity
from classes.zoomActivity import ZoomActivity
import yaml


def config():
	# fetches the configs from the available file
	with open('/Users/dfine/Documents/on-air-sign/config/config.yaml', 'r') as config_file:
		config = yaml.load(config_file, Loader=yaml.CLoader)

		return config


def sr_client():
	# set up schema registry
	sr_conf = config()['schema-registry']
	sr_client = SchemaRegistryClient(sr_conf)

	return sr_client


def camera_activity_deserializer():
	return AvroDeserializer(
		schema_registry_client = sr_client(),
		schema_str = CameraActivity.get_schema(),
		from_dict = CameraActivity.dict_to_camera_activity
		)


def zoom_activity_deserializer():
	return AvroDeserializer(
		schema_registry_client = sr_client(),
		schema_str = ZoomActivity.get_schema(),
		from_dict = ZoomActivity.dict_to_zoom_activity
		)


def camera_activity_serializer():
	return AvroSerializer(
		schema_registry_client = sr_client(),
		schema_str = CameraActivity.get_schema(),
		to_dict = CameraActivity.camera_activity_to_dict
		)


def zoom_activity_serializer():
	return AvroSerializer(
		schema_registry_client = sr_client(),
		schema_str = ZoomActivity.get_schema(),
		to_dict = ZoomActivity.zoom_activity_to_dict
		)


def producer(value_serializer, conf):
	producer_conf = config()[conf] | { 'value.serializer': value_serializer }
	return SerializingProducer(producer_conf)


def consumer(value_deserializer, conf, group_id, topics):
	consumer_conf = config()[conf] | {'value.deserializer': value_deserializer,
										  'group.id': group_id,
										  'auto.offset.reset': 'earliest',
										  'enable.auto.commit': 'false'
										  }

	consumer = DeserializingConsumer(consumer_conf)
	consumer.subscribe(topics)

	return consumer