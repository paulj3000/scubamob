#===============================================================================
# wm.utils.converter
#
# General purpose utility functions
#
# (C) Copyright 2011, Webmetrics Inc. All Rights Reserved
#
# Authors:
#===============================================================================

#===============================================================================
# Imports
#===============================================================================
from datetime import datetime, timedelta
from math import floor
from time import mktime, localtime
from urllib import quote, unquote, urlencode
import calendar
import re
import uuid
import os, tempfile, zipfile
from itertools import izip, cycle

from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.utils.encoding import smart_str

browsers = {
    'FF':       'Firefox',
    'CHROME':   'Chrome',
    'IE':       'Internet Explorer',
    'RIA.IE':   'Internet Explorer'
}
error_types = {
    'internal-exception':   'Internal',
    'content':              'Content',
    'connectivity':         'Connectivity',
    'script-execution':     'Script Execution',
    'script-timeout':       'Script Timeout',
    'script-stopped':       'Script Stopped',
    'script-exception':     'Script Exception',
    'step-timeout':         'Step Timeout',
    'file-download':        'File Download'
}
#===============================================================================
# Class Interface
#===============================================================================
def to_time_string(epoch, format="%H:%M:%S.%f", is_utc=True, decimals=2):
    '''
    Convert epoch seconds to time string
    Default: H:M:S.mS (with 2 decimals in milliseconds)
    Params: is_utc=True: if epoch is in UTC
            decimals=<n>: show <n> decimals in milliseconds
    '''
    try:
        # Disable the millisecond, we handle it separately, '%1f' is as a placeholder
        format = format.replace('%f', '%1f') if decimals else format.replace('.%f','')
        dt = datetime.fromtimestamp(epoch) if not is_utc else datetime.utcfromtimestamp(epoch)
        ### python 2.6 and 2.7 handle the %1f in strftime differently - do the formating ourselves.
        milli = ('%.' + str(decimals) + 'f') % float(dt.microsecond/1000000.0)
        format = format.replace('%1f', milli.replace('0.', '')) if '%1f' in format else format
        result = datetime.strftime(dt, format)
        return result.replace('AM', 'am').replace('PM', 'pm')
    except Exception as ex:
        print ex
        return ""

def to_time_delta_string(interval):
    h,m,s =  interval.__str__().split(".")[0].split(":")
    h,m,s = int(h), int(m), int(s)
    return ("%sh "%h if h > 0 else "") + ("%sm "%m if m > 0  or h > 0 else "") + ("%ss"%s if h == 0 and s != 0 else "")

def ISO8601_to_date(str):
    '''
    Convert 'YYYY-MM-DDT[hh:mm[:ss[.s]][Z]]' to datetime
    Warning: This code has never been tested.
    '''
    if str[-1].isalpha:
        ## throw away time zone for now.
        str=str[:-1]
    year = int(str[0:4])
    month = int(str[5:7])
    day = int(str[8:10])
    hour = int(str[11:13])
    min = int(str[14:16])
    sec = float(str[17:])
    ms = int((sec - floor(sec)) * 1000)
    sec = int(sec)

    return datetime(year,month,day,hour,min,sec,ms)


def to_epoch(dt_str, format="%Y-%m-%d", delta=None, inMilliSec=True):
    '''
    Return epoch time in millisecond
    '''
    dt = datetime.strptime(dt_str, format)
    if delta:
        dt += timedelta(seconds=float(delta))
    # dt is a struct_time in UTC
    # Get epoch time in seconds and return in milliseconds
    epoch = calendar.timegm(dt.timetuple()) + (dt.microsecond/1000000.0)
    return float(epoch*1000) if inMilliSec else float(epoch)

def to_utc_string(dt_str, offset, format="%Y-%m-%dT%H:%M:%S"):
    '''
    Return time string in UTC, given the offset from local time to UTC
    '''
    local_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
    utc_dt = local_dt + timedelta(minutes=int(offset))
    return datetime.strftime(utc_dt, format)

def to_utc_datetime(dt, offset=0, format="%Y-%m-%d %I:%M %p"):
    '''
    Return datetime in UTC, given the offset (minutes) from local time to UTC
    and dt (either string with format, or epoch in seconds)
    '''
    local_dt = datetime.strptime(dt, format) if isinstance(dt, basestring) else datetime.fromtimestamp(dt)
    return local_dt + timedelta(minutes=int(offset))

def to_utc_timestamp():
    return int(calendar.timegm(datetime.utcnow().timetuple()))
 
def to_second(epoch):
    '''
    Convert millisecond epoch to second epoch with decimal number
    Return a string result
    '''
    return str(float(epoch)/1000)

def format_tz(tzOffset):
    '''
    Convert the tzOffset (in minutes) to ISO8601 timezone format
    For example: 420 is "-0700"
    '''
    tzOffset = int(tzOffset);
    sign = "+" if tzOffset < 0 else "-"
    return "%s%02d%02d" % (sign, abs(tzOffset)/60, abs(tzOffset)%60)

def to_KB(bytes):
    return float(bytes)/1024

def format_second(epoch, format="%.2fs", inMilliSec=True):
    try:
        converted = to_second(epoch) if inMilliSec else epoch
        return format % float(converted)
    except Exception:
        return ''

def format_percentage(percent, format="%.2f%%", inPercent=True):
    try:
        converted = float(percent)*100 if not inPercent else percent
        return format % float(converted)
    except Exception:
        return ''

def is_valid_number(value):
    '''
    Validate if a string is a valid number (both integer and float)
    '''
    try:
        float(value)
        return True
    except:
        return False

def is_valid_guid(guid):
    '''
    Validate if it is a valid guid, 32 (or 36 with hyphens) characters in hex digit
    '''

    try:
        uuid.UUID(guid)
        return True
    except:
        return False
    
def guid_with_dash(guid):
    '''
    Add dashes to guid
    '''
    guid = guid.strip().lower()
    if is_valid_guid(guid):
        id = uuid.UUID('%s' % guid)
        return str(id)
    else:
        return guid
    
def guid_without_dash(guid):
    '''
    Remove dashes from a valid guid, for example: a9b5ed7c-c84f-11e0-913a-000c29901eb8
    '''
    guid = guid.strip().lower()
    if is_valid_guid(guid):
        return guid.replace('-', '')
    else:
        return guid

def get_browser_full_name(name):
    try:
        from wm.agents.models import BrowserType
        return BrowserType.objects.get(code=name.strip()).label
    except Exception, ex:
        print_u("Get browser full name failed: %s" % ex)
        return browsers['FF']

def get_error_type(type):
    try:
        return error_types[type]
    except:
        return error_types['internal-exception']

def to_date_string(start_date, end_date, date_ref=''):
    '''
    start_date and end_date are in ISO8601 format 'YYYY-MM-DDTHH:MM:SS'
    Return a single date string 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS - YYYY-MM-DD HH:MM:SS'
    if two base dates are different
    '''
    
    sdate_array = re.search('([-|\d]+)T([-|\d]+)', start_date)
    sdate_base = sdate_array.group(1) if sdate_array else ''
    edate_array = re.search('([-|\d]+)T([-|\d]+)', end_date)
    edate_base = edate_array.group(1) if edate_array else ''
    if not sdate_base == '' and not edate_base == '':
        if sdate_base == edate_base:
            return [sdate_base]
        else:
            # One exception for Last 24 Hours, if start_date=2012-03-07 23:59:59, end_date=2012-03-08 23:59:59
            # It's more understandable to return 2012-03-08
            return [edate_base] if date_ref == 'last_24_hours' else [start_date.replace('T', ' '), end_date.replace('T', ' ')]
    else:
        return []
    
def to_status_string(status=0):
    '''
    Return sample's status string: Success=0, Warning=1, Error=2
    '''
    return ['Success', 'Warning', 'Error'][int(status)]

def send_zipfile(fname, floc):
    '''
    Send a file through Django without loading the whole file into memory at once.
    The FileWrapper will turn the file object into an iterator for chunks of 8KB
    '''
    fpath = floc + fname
    zip_file = file(fpath)
    wrapper = FileWrapper(zip_file)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    response['Content-Length'] = os.path.getsize(fpath)
    return response

def send_contents(fname, contents, content_type='application/zip'):
    '''
    Send contents directly through HttpResponse (for image file)
    '''
    temp = tempfile.TemporaryFile()
    temp.write(contents)
    temp.seek(0)
    response = HttpResponse(FileWrapper(temp), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    response['Content-Length'] = len(contents)
    return response

def print_u(str=''):
    # Print unicode string
    print smart_str(str)

def get_default_tz_offset():
    '''
    Return timezone offset in minutes (from UTC) with respect to daylight saving
    '''
    if localtime().tm_isdst == 1:
        return settings.REPORT_DEFAULT_TZ_OFFSET - settings.DST_OFFSET
    else:
        return settings.REPORT_DEFAULT_TZ_OFFSET

def filter_by_account(records, squared_id):
    '''
    Iterate through array of registry records to find the one matching account's squared_id
    because one email may associate with more than 1 account
    '''
    try:
        for record in records:
            if record.get('accountGUID', '') == squared_id:
                return record
        return None
    except Exception, ex:
        print_u("Filter by account failed: %s" % ex)
        return None

def is_subscribed(subscriptions, application='monitor_report'):
    '''
    Iterate through array of subscriptions to find out if the application's subscribe is True/False
    '''
    try:
        for sub in subscriptions:
            if sub.get('application', '') == application:
                return sub.get('subscribe', True)
        return True
    except Exception, ex:
        print_u("Checking subscribed failed: %s" % ex)
        return True     # worst case, still want to send email


def xor_crypt_string(data, key='Password1!'):
    '''
    Iterate over every letter of data, and XOR it with the key
    '''
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))


def encipher(data=''):
    '''
    Encipher the query string by XOR and base64_codec
    '''
    try:
        if data:
            return xor_crypt_string(data + '&passed=True').encode("base64_codec").replace('\n', '')
        else:
            return None
    except Exception, ex:
        print_u("Encipher failed: %s" % ex)
        return None


def decipher(data=''):
    '''
    Decipher the encrypted string by base64_codec and XOR
    '''
    try:
        decrypted = xor_crypt_string(data.replace('nEWLine', '\n').decode("base64_codec"))
        if decrypted.endswith('&passed=True'):
            return decrypted.replace('&passed=True', '')
        else:
            return None
    except Exception, ex:
        print_u("Decipher failed: %s" % ex)
        return None

def escape(data=''):
    '''
    Escape single and double quotes
    '''
    try:
        return data.replace("'", "\\'").replace('"', '\\"')
    except Exception, ex:
        print_u("Escape single and double quotes failed: %s" % ex)
        return None
        

def is_authorized(us_request, monitor_id=''):
    '''
    Verify if the monitor, from the monitorId, actually belongs to the account in the request
    '''
    try:
        return True if monitor_id and us_request.account.monitors.filter(id=guid_with_dash(monitor_id)).first() else False
    except Exception, ex:
        print_u("Authorize the monitor %s belong the account failed: %s" % (monitorId, ex))
        return True

def authorize_action(us_request, monitor_id='', redirect=''):
    '''
    Return to 404 Redirect Page if authorization of a monitor fails
    '''
    from wm.home.views import view404_redirect
    redirect = quote(redirect or us_request.META.get('PATH_INFO', ''))
    return view404_redirect(us_request, {'login_redirect': redirect}) if not is_authorized(us_request, monitor_id) else None


