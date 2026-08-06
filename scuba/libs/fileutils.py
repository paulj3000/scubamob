import os
import requests

from scuba.sitesettings.models import SystemApi
from scuba.settings import AWS_S3_BUCKET
from scuba.libs.stringutils import StringUtils
from scuba.libs.exceptions import InvalidHttpStatusCode
from scuba.libs.aws.s3 import S3


class FileUtils:
    @staticmethod
    def write_to_file(filename, content):
        f = open(filename, "wb")
        f.write(content.encode())
        f.close()

    @staticmethod
    def upload_file_to_s3(filename, content_type, content, **kwargs):
        headers = {
            'ContentType': content_type,
        }

        headers.update(kwargs.get('headers', {}))

        # generate the data to send over to S3
        S3.upload_raw_data(filename, content, bucket=AWS_S3_BUCKET, **headers)

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
