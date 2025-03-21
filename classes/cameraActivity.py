class CameraActivity(object):
    """CameraActivity stores the deserialized Avro record for the Kafka key."""
    # Use __slots__ to explicitly declare all data members.
    __slots__ = [
        "camera_ts", 
        "camera_status",
        "application_id"
    ]

    @staticmethod
    def get_schema():
        with open('./avro/cameraActivity.avsc', 'r') as handle:
            return handle.read()
    
    def __init__(self, camera_ts, camera_status, application_id):
        self.camera_ts      = camera_ts
        self.camera_status  = camera_status
        self.application_id = application_id

    @staticmethod
    def dict_to_camera_activity(obj, ctx=None):
        return CameraActivity(
                obj['camera_ts'],
                obj['camera_status'],
                obj['application_id']    
            )

    @staticmethod
    def camera_activity_to_dict(camera_activity, ctx=None):
        return CameraActivity.to_dict(camera_activity)

    def to_dict(self):
        return dict(
                    camera_ts      = self.camera_ts, 
                    camera_status  = self.camera_status,
                    application_id = self.application_id
                )