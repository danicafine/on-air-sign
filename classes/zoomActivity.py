class ZoomActivity(object):
    """ZoomActivity stores the deserialized Avro record for the Kafka key."""
    # Use __slots__ to explicitly declare all data members.
    __slots__ = [
        "zoom_ts",
        "zoom_status"
    ]

    @staticmethod
    def get_schema():
        with open('./avro/zoomActivity.avsc', 'r') as handle:
            return handle.read()
    
    def __init__(self, zoom_ts, zoom_status):
        self.zoom_ts     = zoom_ts
        self.zoom_status = zoom_status

    @staticmethod
    def dict_to_zoom_activity(obj, ctx=None):
        return ZoomActivity(
                obj['zoom_ts'],
                obj['zoom_status']  
            )

    @staticmethod
    def zoom_activity_to_dict(zoom_activity, ctx=None):
        return ZoomActivity.to_dict(zoom_activity)

    def to_dict(self):
        return dict(
                    zoom_ts     = self.zoom_ts,
                    zoom_status = self.zoom_status
                )