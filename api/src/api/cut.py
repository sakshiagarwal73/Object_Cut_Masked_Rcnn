from flask import request, jsonify

from src import *
from src.helper import image_utils
from src.helper.response_maker import make_response
from src.scripts.run import instance_segmentation_api


def post():
    try:
        body = request.json

        required_parameters = ['objects']
        if not all(x in body for x in required_parameters):
            return jsonify(make_response(True, message=f'{required_parameters} body parameters are required.')), 400

        if not all(o in COCO_INSTANCE_CATEGORY_NAMES for o in body['objects']):
            return jsonify(make_response(True, message='One or more objects from the list will not be detected.')), 400

        if bool('image_url' in body) == bool('image_base64' in body):
            return jsonify(make_response(True, message='image_url (x)or image_base64 has to be specified')), 400

        if 'image_url' in body:
            image_path = image_utils.download(body['image_url'])
        elif 'image_base64' in body:
            image_path = image_utils.decode(body['image_base64'])
        else:
            image_path = None

        if not image_path:
            return jsonify(make_response(True, message='Wrong image specified.')), 400

        output_image_path = instance_segmentation_api(image_path, body['objects'])
        image_utils.remove_white(output_image_path)
	encoded_string = image_utils.encode(output_image_path)

        return jsonify(make_response(False, image_base64=encoded_string)), 200

    except Exception as e:
        return jsonify(make_response(True, message=f'Unexpected error: {e}')), 400
