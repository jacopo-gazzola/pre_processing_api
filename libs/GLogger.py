import config.GLogger_config as config
from datetime import datetime
import os

class Logger:

    def __init__(self, log_filename, log_folder = config.logs_default_folder):
        self.log_file = open(os.path.join(log_folder, log_filename + ".grlog"), "a")

    def Info(self, text):
        self.__Out("INFO", text)

    def Warn(self, text):
        self.__Out("WARN", text)

    def Error(self, text):
        self.__Out("ERR!", text)

    def Log(self, text):
        self.__Out(" >> ", text)

    def Success(self, text):
        self.__Out("SUCC", text)

    def LogStart(self):
        self.__Out("[ ===== ] LOG START [ ===== ]")

    def LogEnd(self):
        self.__Out("[ ===== ]  LOG END  [ ===== ]")

    def __Out(self, prefix, text):
        self.log_file.write(f"({datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}) [{prefix}] {text}\n")
        self.log_file.flush()