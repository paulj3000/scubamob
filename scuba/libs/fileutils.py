import os
import json
import requests

from scuba.sitesettings.models import SystemApi
from scuba.settings import AWS_S3_BUCKET
from scuba.libs.stringutils import StringUtils
from scuba.libs.exceptions import InvalidHttpStatusCode


class FileUtils:
    @staticmethod
    def write_to_file(filename, content):
        f = open(filename, "wb")
        f.write(content.encode())
        f.close()

    @staticmethod
    def upload_file_to_s3(filename, content_type, content):
        url = SystemApi.get_s3_upload()

        data = {
            'headers':
                json.dumps([{
                    "key": "ContentType",
                    "value": content_type,
                }, {
                    "key": "ContentType",
                    "value": content_type,
                }]),
            'bucket': AWS_S3_BUCKET,
            'key': filename,
        }

        headers = {'Content-Type': 'multipart/form-data'}

        files = {'file': content}
        resp = requests.post(url, files=files, data=data)

        if resp.status_code < 200 or resp.status_code > 299:
            raise InvalidHttpStatusCode(resp.status_code, resp.text)

        return resp

    @staticmethod
    def delete_file_from_s3(filename):
        url = SystemApi.get_s3_delete()

        data = {
            'bucket': AWS_S3_BUCKET,
            'key': filename,
        }

        resp = requests.post(url, json=data)

        if resp.status_code < 200 or resp.status_code > 299:
            raise InvalidHttpStatusCode(resp.status_code, resp.text)

        return resp


    @staticmethod
    def create_temp_dir(dir_base):
        tmp_dir = StringUtils.generate_random_string(6)
        layout_temp_dir = os.path.join(dir_base, tmp_dir)

        # create the directory
        os.mkdir(layout_temp_dir)

        return layout_temp_dir
