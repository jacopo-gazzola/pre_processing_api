import os
import sys

cwd = os.getcwd()

P_CONN  = ("ip_addr",3306,"usr","pwd","pre_processing") #pre_processing database
P_CONN2 = ("ip_addr",3306,"usr","pwd","networks") #networks mysql database
P_CONN4 = ("ip_addr",5432,"usr","pwd","networks") #networks postgres database

if sys.platform == "linux":
    files_folder = os.path.join(cwd, "files/")

elif sys.platform == "win32":
    files_folder = os.path.join(cwd, "files\\")
