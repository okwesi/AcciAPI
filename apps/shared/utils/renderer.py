from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """
    Custom renderer to handle list of dictionaries by encapsulating them in an additional dictionary.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            data = {'results': data}
        return super().render(data, accepted_media_type, renderer_context)
