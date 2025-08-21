from config.constants import *

import os
import json

# checks config file
def is_config_file_present(directory: str = os.getcwd()):
  # check if file exists and is file
  file_path = os.path.join(directory, CONFIGURATION_FILE_NAME)

  return os.path.exists(file_path) and os.path.isfile(file_path)

# loads config file
def get_config_file_content(directory: str = os.getcwd()):
  file_path = os.path.join(directory, CONFIGURATION_FILE_NAME)
  
  with open(file_path, 'r') as file:
    content = file.read()

  return json.loads(content)
