import sys

from libs.GLogger import Logger

logger = Logger("GResponse")

if 'flask' in sys.modules:
    from flask import jsonify 
else:
    logger.Warn("Flask module not found (ok for clients)")



class Response:

    result_error    =   "err"
    result_success  =   "ok"

    code_error            = 401
    code_success          = 200
    code_import_not_found = 201



    @classmethod
    def Error(cls, message = "Something went wrong", **data):

        '''
        Default response for generic errors
        
        @params
        message : message in addition to the status code

        @return
        flask.Response object
        '''
        
        resp = {
            "result"    :   cls.code_error,
            "message"   :   message,
        }

        for key in data.keys():
            resp[key] = data[key]

        resp = jsonify(resp)
        resp.status_code = cls.code_error

        return resp



    @classmethod
    def Success(cls, message = "Success", **data):

        '''
        Default response for generic success
        
        @params
        message : message in addition to the status code

        @return
        flask.Response object
        '''

        resp = {
            "result"    :   cls.result_success,
            "message"   :   message,
        }

        for key in data.keys():
            resp[key] = data[key]

        resp = jsonify(resp)
        resp.status_code = cls.code_success

        return resp

    
    
    @classmethod
    def Import(cls, message = "Retrieved import", imp = '', **data):

        '''
        Default response for Scaling machines' import requests
        
        @params
        message : message in addition to the status code
        imp     : name of the imported file

        @return
        flask.Response object
        '''

        resp = {
            "result"    :   cls.result_success,
            "message"   :   message,
            "import"    :   imp,
        }

        for key in data.keys():
            resp[key] = data[key]

        resp = jsonify(resp)

        if imp == '':   resp.status_code = cls.code_import_not_found
        else:           resp.status_code = cls.code_success

        return resp
