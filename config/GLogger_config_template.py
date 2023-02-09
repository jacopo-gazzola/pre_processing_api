import os
import sys

cwd = os.getcwd()

if sys.platform == "linux":
    logs_default_folder = os.path.join(cwd, "logs/")

elif sys.platform == "win32":
    logs_default_folder = os.path.join(cwd, "logs\\")