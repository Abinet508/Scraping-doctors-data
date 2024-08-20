import datetime
import json
from flask_restful import Resource
from http import HTTPStatus
from flask import make_response, send_file
import os


class Resource_API(Resource):
    """
    SampleAPI class that returns doctors_data.xml as response to the client
    Args:
        Resource (Resource): Resource class from flask_restful
    """
    def __init__(self, requested_file):
        self.requested_file = requested_file
        self.file_path = os.path.join(os.path.dirname(__file__), "documents")
        self.last_modified_json_file = os.path.join(self.file_path, "last_modified.json")
    def get(self):
        """
        Function that returns doctors_data.xml file as response to the client
        Returns:
            tuple: tuple containing response data and status code
        """
        try:
            if os.path.exists(os.path.join(self.file_path, self.requested_file)):
                requested_file = os.path.join(self.file_path, self.requested_file)
                if not requested_file.endswith(".xml") and not requested_file.endswith(".json"):
                    requested_file = os.path.join(self.file_path, "doctors_data.xml")
                trimmed_filename= self.requested_file.split(".")[0]
                if requested_file.endswith(".xml"):
                    if os.path.exists(self.last_modified_json_file):
                        with open(self.last_modified_json_file, "r") as f:
                            last_modified_date = json.load(f)["xml_data"][trimmed_filename]
                    else:
                        last_modified = datetime.datetime.now()
                        last_modified_date = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    print(last_modified_date)
                    return send_file(requested_file, as_attachment=False,download_name=f"{trimmed_filename}-{last_modified_date}.xml")
                elif requested_file.endswith(".json"):
                    if os.path.exists(self.last_modified_json_file):
                        with open(self.last_modified_json_file, "r") as f:
                            last_modified_date = json.load(f)["json_data"][trimmed_filename]
                    else:
                        last_modified = datetime.datetime.now()
                        last_modified_date = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    return send_file(requested_file, as_attachment=False,download_name=f"{trimmed_filename}-{last_modified_date}.json")
            return make_response({"message": "The requested URL was not found on the server"}, HTTPStatus.NOT_FOUND)
        
        except Exception as e:
            print(e)
            return make_response({"message": "Internal Server Error"}, HTTPStatus.INTERNAL_SERVER_ERROR)