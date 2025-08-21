from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

from builtins.builtins import *

# THIS CODE IS TEST

aliases = {
  "base": "C:/Users/User/Desktop/programming language/examples",
  "std": "C:/Users/User/Desktop/programming language/stdlib"
}

path = "C:/Users/User/Desktop/programming language/examples/loops.br"

resolver = Resolver(aliases)
resolver.resolve_modules(path)
modules = resolver.sort_modules()
interpreter = Interpreter(resolver)
interpreter.load_modules(modules)
interpreter.register_builtins(builtins)
interpreter.execute()
