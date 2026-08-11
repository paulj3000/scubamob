import os

from scuba.settings import AWS_S3_BUCKET
from scuba.libs.stringutils import StringUtils
from scuba.libs.aws.s3 import S3


class FileUtils:
    @staticmethod
    def write_to_file(filename, content):
        # reject any path-traversal component -- filename comes straight
        # from the caller with no base directory to sandbox it against.
        if '..' in filename.replace('\\', '/').split('/'):
            raise ValueError(f"Invalid filename: {filename}")

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
        S3.delete_file(filename, bucket=AWS_S3_BUCKET)

    @staticmethod
    def create_temp_dir(dir_base):
        tmp_dir = StringUtils.generate_random_string(6)
        layout_temp_dir = os.path.join(dir_base, tmp_dir)

        # create the directory
        os.mkdir(layout_temp_dir)

        return layout_temp_dir
