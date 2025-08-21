from config.config import get_config
from config.constants import *

from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

from builtins.builtins import *

# THIS CODE IS TEST

aliases = {
  "base": "C:/Users/User/Desktop/programming language/examples",
  "std": "C:/Users/User/Desktop/programming language/stdlib"
}

path = "C:/Users/User/Desktop/programming language/examples/loops.br"

def execute_code():
  config = get_config()

  # resolve modules dependency graph
  resolver = Resolver(config[CONFIGURATION_ALIASES_KEY])
  resolver.resolve_modules(config[CONFIGURATION_ENTRYPOINT_KEY])
  
  # get topologically sorted modules
  modules = resolver.sort_modules()

  # execute modules
  interpreter = Interpreter(resolver)
  interpreter.load_modules(modules)
  interpreter.register_builtins(builtins)
  interpreter.execute()
