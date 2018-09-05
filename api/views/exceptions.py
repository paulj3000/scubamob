VALID_FIELDS    = []
class APIException(Exception):
    def __init__(self,message=None, **args):
        self.json = {'errors' : {} }
        try:
            if not args.get('code', None):
                self.json['errors']['Error'] = self.DESCRIPTION
        except AttributeError:
            self.json['errors']['Error'] = "%s"%self.__class__
        
        if self.__dict__.get('ERROR_CODE'):
            self.json['errors']['ErrorCode'] = self.ERROR_CODE

        self.json['errors'].update(args)

        ## make sure we're setting our message
        if message:
            self.json['errors']['message']  = message

        super(APIException, self).__init__(message)

# instantiate our invalid field types
class InvalidFieldException(APIException):
    DESCRIPTION = "Invalid field name. Valid field names are %s: "%(" ".join(VALID_FIELDS))

class InvalidIdException(APIException):
    DESCRIPTION = "Invalid Id"
    
class InvalidValueException(APIException):
    DESCRIPTION = "Invalid Value"

class RequiredFieldMissingException(APIException):
    DESCRIPTION = "A required field is missing."

class CannotCompleteAction(APIException):
    DESCRIPTION = "Cannot complete request."

class CatastrophicException(APIException):
    DESCRIPTION = "System Error"

class InvalidFieldException(APIException):
    DESCRIPTION = "Invalid field name. Valid field names are %s: "%(" ".join(VALID_FIELDS))

#===============================================================================
# Define error codes
#===============================================================================
class APIErrorCodes():
    def __init__(self):
        self.code = 'code'
        self.message = 'message'
        self.field = 'field'

    def not_found(self, field, monitor_id):
        message = "%s with Id '%s' not found."%(field, monitor_id)
        return { self.code:  'MON_0001', self.message: message   }

    def duplicate(self, name):
        return { self.code:  'MON_0002', self.message: "Duplicate name '%s' found."%name  }

    def missing_fields(self, missing_fields, valid_fields = [], optional_fields = []):
        if len(missing_fields) == 1:
            message = "%s is a required field." % missing_fields[0]
        else:
            message = "%s are required fields." % ', '.join(missing_fields)

        # return our message
        retval = { self.code:  'MON_0003', self.message: message }
        if len(valid_fields):
            retval.update({ 'validFields': valid_fields})
        if len(optional_fields):
            retval.update({ 'optionalFields': optional_fields})

        return retval

    def invalid_value(self, value, field, valid_values = []):
        message = "'%s' is an invalid value."% str(value)
        retval = { 'validValues': valid_values } if len(valid_values) else {}
        retval.update({ self.code: 'MON_0004', self.message: message, self.field: field })
        return retval

    def invalid_field_type(self, value, field, expected):
        message = "'%s' is an invalid value type.  Type '%s' expected" % (str(value), str(expected))
        return { self.code:  'MON_0005', self.message: message, 'field': field     }

    def invalid_fields(self, invalid_fields):
        if len(invalid_fields) == 1:
            message = "%s is an invalid field" % invalid_fields[0]
        else:
            message = "%s are invalid fields" % ', '.join(invalid_fields)

        # return our message
        retval = { self.code:  'MON_0006', 'message': message }
        return retval

    def id_not_supplied(self, field):
        message = "Valid %s id not supplied" % field
        return { self.code:  'MON_0007', self.message: message   }

    def no_data_supplied_post(self):
        message = "Empty body received in POST"
        return { self.code:  'MON_0008', self.message: message   }

    def no_data_supplied_put(self):
        message = "Empty body received in PUT"
        return { self.code:  'MON_0009', self.message: message   }

    def cannot_complete_request(self, field, message):
        return { self.code:  'MON_0010', self.message: message   }

    def system_error(self):
        return { self.code:  'MON_9999', self.message: 'An internal error has occured'     } 
