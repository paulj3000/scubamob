import pprint, os, sys
from datetime import datetime
from threading import Thread
from django.conf import settings
from django.utils import simplejson
from django.utils.encoding import smart_str

from utils.jsonresponse import JSONEncoder

DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"
CRITICAL = "CRITICAL"
ALERT = "ALERT"
EMERGENCY = "EMERGENCY"

class Log:
    ALERT_LEVELS = (DEBUG,INFO,WARN,ERROR,CRITICAL,ALERT,EMERGENCY)

    def __init__(self, module="django", always_log=False, send_to_loggly=True):
        self.log_file_pathname = os.path.join(settings.LOG_FOLDER, "monitoring.%s.log"%module)
        self.always_log = always_log
        self.send_to_loggly = send_to_loggly

    ### Recommended fields for object (none of these fields are required - but if present should use the label below) :
    ###   error_code:  Unique error code for each object (3 letters and 3 numbers)
    ###                  AGN (Agents)
    ###                  API (Api Call)
    ###                  ACM (Account Management)
    ###                  CON (Configuration)
    ###                  LOG (login)
    ###                  MCR (Create Monitor)
    ###                  MCO (Monitor Console)
    ###                  MON (other MONitor related processes)
    ###                  MSC (Miscellaneous)
    ###                  RED (Redis)
    ###                  ... add your own code and document here.
    ###   location:    MODULE.OBJECT.FUNCTION from source code
    ###   description: Description of error/info 
    ###   account:     name of account
    ###   accountId:   id of account
    ###   crowdId:     Crowd id of account (single sign on)
    ###   monitor:     name of monitor
    ###   monitorId:   id of monitor
    ###   exception:   the exception object
    ###   request:     the django request object
    ###   response:    the django response object

    def exception(self, ex, alert_level=DEBUG, error_code='EXC001'):
        import traceback
        exception_object = { 'error_code': error_code, 'Exception' : '%s'%ex, 'Traceback' : traceback.format_exc() }
        self.message(exception_object,alert_level);
    
    def object(self, obj, alert_level=DEBUG):
        if self.__loggable(obj, alert_level):
            self.__writerawlog(alert_level, obj)
    message=object

    def __loggable(self, obj, alert_level):
        if alert_level not in Log.ALERT_LEVELS:
            raise ValueError("Invalid alert level %s"%alert_level); 
        return Log.ALERT_LEVELS.index(alert_level) >= Log.ALERT_LEVELS.index(settings.ALERT_LEVEL)

    def __writerawlog(self, alert_level, log_obj):

        try:
            if not self.send_to_loggly:
                pass
            elif not settings.DEBUG:
                ## can't import this in header because external_connections uses this module.
                from wm.utils.external_connections import get_external_data
                meta_data = settings.EXTERNAL_INTERFACES['LOGGLY_ADD']
                if type(log_obj) == dict:
                    log_obj['host'] = os.uname()[1]
                log_thread = Thread(target=get_external_data, args=(meta_data,), kwargs={'params':{ 'alert_level' : alert_level, 'data' : log_obj}})
                log_thread.start()
            else:
                sys.stderr.write("In debug mode: no data sent to loggly\n")

        except:
            file = open(os.path.join(settings.PROJECT_ROOT,"../logs/", "LOG.log"),'a')
            file.write("{1} {0:<10s}:Failed to send message to loggly {2}\n". format(ERROR,datetime.now().ctime(),log_obj))
            file.close();

        # Trim the log if necessary
        if type(log_obj)==dict and log_obj.get('response') and isinstance(log_obj.get('response'),basestring):
            log_obj['response'] = log_obj['response'][:200] if not settings.FULL_LOGGING else log_obj['response']

        if not self.always_log and settings.DEBUG:
            print(smart_str("{1} {0:<10s}: {2}\n".format(alert_level,datetime.now().ctime(),log_obj)))
        else:
            file = open(self.log_file_pathname,'a');
            file.write(smart_str("{1} {0:<10s}: {2}\n".format(alert_level,datetime.now().ctime(),log_obj)))
            file.close();
