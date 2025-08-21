from config.exceptions import *
from config.constants import *
from config.file import *

import sys
import os

def get_config(directory: str = os.getcwd()):
  # require config file
  if not is_config_file_present(directory):
    raise ConfigError(f"{CONFIGURATION_FILE_NAME} is not found")

  # get content
  configuration_file = get_config_file_content(directory)

  # load fields
  entry = get_config_entry(configuration_file, directory)
  aliases = get_config_aliases(configuration_file)

  # return normalized config
  return ({
    CONFIGURATION_ENTRYPOINT_KEY: entry,
    CONFIGURATION_ALIASES_KEY: aliases
  })

# load fields methods
def get_config_entry(configuration_file: dict, current_directory: str):
  # get command line arguments
  args = sys.argv[1:]

  # command line path has highest priority
  if len(args):
    # get entry from relative path
    entrypoint = os.path.abspath(os.path.join(current_directory, args[0]))

    if not os.path.exists(entrypoint):
      raise ConfigError(f'Entrypoint is invalid')
    
    return entrypoint

  # check configuration file
  if not CONFIGURATION_ENTRYPOINT_KEY in configuration_file:
    raise ConfigError(f'"{CONFIGURATION_ENTRYPOINT_KEY}" is not set')

  entrypoint = configuration_file[CONFIGURATION_ENTRYPOINT_KEY]

  if not os.path.isabs(entrypoint):
    entrypoint = os.path.abspath(os.path.join(current_directory, entrypoint))

  return entrypoint

def get_config_aliases(configuration_file: dict):
  # if aliases are missed
  if CONFIGURATION_ALIASES_KEY not in configuration_file:
    return dict()
  
  aliases = configuration_file[CONFIGURATION_ALIASES_KEY]
  if not isinstance(aliases, dict):
    raise ConfigError(f'"{CONFIGURATION_ALIASES_KEY}" has to be an object')  
  
  return aliases
    