import os
import sys
import time

from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename

from libs.GLogger import Logger
logger = Logger("pre_processing_api")

from libs.GResponse import Response
import libs.db_connector as db_connector

import config.pre_processing_api_config as config



app = Flask(__name__)

api = Api(app)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 *1024 #MB = x * 1024 * 1024



class check_import(Resource):

    def __init__(self):
        self.xdb = db_connector.mysql(*config.P_CONN)
        self.check_query =  """SELECT * FROM import WHERE status = 0 ORDER BY id ASC"""
        self.update_query = """UPDATE import SET status=1 WHERE id = %s"""

    def get(self):

        try:
            to_process = self.xdb.SAFE_QDB_FULL_ALT(self.check_query,())
        except:
            logger.Error("Database connection error")
            return Response.Error(message="Database connection error")
            
        if len(to_process) > 0:
            self.xdb.SAFE_QDB_FULL_ALT(self.update_query,(to_process[0]["id"]))
            file_name = to_process[0]["nome_file"]

            try:
                return Response.Import(imp = to_process[0])

            except Exception as e:
                logger.Error(f"Unable to send task: {e}")
                return Response.Error(message=f"Unable to send task\nDetails: {e}")

        else:
            return Response.Import()



class upload_results_info(Resource):

    def __init__(self):
        self.xdb = db_connector.mysql(*config.P_CONN)
        self.update_query_suc = """UPDATE import SET status=2 WHERE id = %s"""
        self.update_query_err = """UPDATE import SET status=3 WHERE id = %s"""

    def post(self):

        req_json = request.get_json()

        logger.Info(f"Got results info: {req_json}")

        if req_json['pproc_status'] == 'not_found':
            self.xdb.SAFE_QDB_FULL(self.update_query_err,(req_json["id_import"]))

        if req_json["pproc_status"]=='Complete' and req_json["gr_resp_status"] == "ok":    
            self.xdb.SAFE_QDB_FULL(self.update_query_suc,(req_json["id_import"]))
            
        elif req_json["pproc_status"]=='Complete' and req_json["gr_resp_status"] == "err":
            self.xdb.SAFE_QDB_FULL(self.update_query_err,(req_json["id_import"]))
            
        else:
            self.xdb.SAFE_QDB_FULL(self.update_query_err,(req_json["id_import"]))

        return Response.Success()



class upload_results(Resource):

    def __init__(self):
        self.ALLOWED_EXTENSIONS = set(['csv', 'txt'])
    
    def allowed_file(self,filename):
        return '.' in filename and filename.split('.')[-1].lower() in self.ALLOWED_EXTENSIONS

    def post(self):

        files = request.files
        failed_files = []
        
        for file in files.values():
            file_path = os.path.join(config.files_folder, file.filename)
            if file and self.allowed_file(file.filename):
                logger.Success(f"Saving result file: {file_path}")
                file.save(file_path)
            else:
                logger.Error(f"Error saving result file: {file_path}")
                failed_files.append(file)
        
        if len(failed_files) == 0:
            return Response.Success()
        else:
            return Response.Error(message=f"Some files were not uploaded, please retry ({', '.join([file.name for file in failed_files])})")



class download_file(Resource):

    def get(self):
        req_json = request.get_json()
        file_name = req_json["file"]
        logger.Info(f"{request.remote_addr} is downloading {file_name}")
        return send_from_directory(config.files_folder, file_name, as_attachment = True)



class upload_files(Resource):
    
    def __init__(self):
        self.ALLOWED_EXTENSIONS = set(['csv'])
        self.filenames = []

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.',1)[1].lower() in self.ALLOWED_EXTENSIONS

    def post(self):

        for key in ('process', 'codice', 'out_version', 'response_url'):
            if key not in request.form.keys():

                logger.Error(f"[upload_files] Missing parameters in request ({key})")
                return Response.Error(message=f"Missing parameters in request ({key})")

        if 'files[]' not in request.files:

            logger.Error("[upload_files] Missing files in request")
            return Response.Error(message="Missing files in request")

        files = request.files.getlist('files[]')
        
        for file in files:
            if file and self.allowed_file(file.filename):
                timestr     = time.strftime("%Y%m%d_%H%M%S")
                filename    = secure_filename(file.filename)

                newname = f"{timestr}_{filename}"
                full_file_path = os.path.join(config.files_folder, newname)

                file.save(full_file_path)
                self.filenames.append(newname)
            
            else:
                return Response.Error(message=f"Some files were not uploaded, please retry ({file.filename})")

        nome_file = ";".join(self.filenames)
        status = "0"
        process = request.form.get('process')
        gr_codice = request.form.get('codice')
        gr_nodi_version = request.form.get('nodi_version') if 'nodi_version' in request.form.keys() else "v1"
        gr_auth_version = request.form.get('out_version')
        gr_response_url = request.form.get('response_url')
        
        db_object = db_connector.mysql(*config.P_CONN) #connessione a DB
        
        db_object.SAFE_QDB_FULL("""INSERT INTO import VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)""",(gr_codice,
                                                                                            gr_auth_version,
                                                                                            gr_nodi_version, 
                                                                                            gr_response_url,
                                                                                            nome_file,
                                                                                            process,
                                                                                            status))
        
        return Response.Success()

api.add_resource(upload_files, '/upload_files')
api.add_resource(check_import, '/check_import')
api.add_resource(download_file, '/download_file')
api.add_resource(upload_results, '/upload_results')
api.add_resource(upload_results_info, '/upload_results_info')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="172.21.10.20",port=5000,debug=True)
