from config.exceptions import *
from config.file import *
from config.constants import *

def get_config(directory: str = os.getcwd()):
  # check config file
  if not is_config_file_present(directory):
    raise ConfigError(f"{CONFIGURATION_FILE_NAME} is not found")

  # get content
  configs = get_config_file_content(directory)

  # validate configs
  if not CONFIGURATION_ENTRYPOINT_KEY in configs:
    raise ConfigError(f'"{CONFIGURATION_ENTRYPOINT_KEY}" is not set')
  
  entrypoint = configs[CONFIGURATION_ENTRYPOINT_KEY]
  aliases = configs[CONFIGURATION_ALIASES_KEY] or {}

  # return normalized config
  return ({
    CONFIGURATION_ENTRYPOINT_KEY: entrypoint,
    CONFIGURATION_ALIASES_KEY: aliases
  })
