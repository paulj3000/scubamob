# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import string
import time
import random


class StringUtils:
    """ Simple class to generate strings and other string objects """
    @staticmethod
    def generate_random_string(string_length):
        return ''.join(random.choices(string.ascii_uppercase + \
            string.digits, k=string_length))

    @staticmethod
    def generate_random_string_case_insensitive(string_length):
        chars = string.ascii_uppercase + \
                string.ascii_lowercase + \
                string.digits
        return ''.join(random.choices(chars, k=string_length))

    @staticmethod
    def generate_random_number(string_length):
        """ generate a random number """
        return ''.join(random.choices(string.digits, k=string_length))

    @staticmethod
    def generate_time_string():
        """ generate_time_string

        generate a random number """
        return str(int(time.time()))

    @staticmethod
    def generate_short_id(cls, key_length, prefix, key='short_id'):
        ''' generate_short_id

        generate a unique short id. Make sure it does not collide with
        another short id from another section '''
        def gen():
            key = [random.choice(string.digits) for i in range(key_length)]

            # a quick little function to generate the key
            return prefix + ''.join(key)

        # do the query
        to_query = {}
        to_query[key] = gen()

        while cls.objects.filter(**to_query).count():
            to_query[key] = gen()

        # return the generated id
        return to_query[key]

    @staticmethod
    def get_random_password_string(length):
        """ get_random_password_string

        # get random string password with letters, digits, and symbols
        """
        password_characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(password_characters) for i in range(length))

    @staticmethod
    def generate_url_from_string(to_convert):
        """ generate_url_from_string

        convert a string to something URL appropriate
        """
        title = re.sub(r'[^\w -]+', '', to_convert)
        return re.sub(r'(-{2,})', '-', title.replace(' ', '-')).lower()
