from lexer.lexer import Lexer
from parser.parser import Parser
from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

from stdlib.builtin.builtins import *

# THIS CODE IS TEST

aliases = {
  "base": "C:/Users/User/Desktop/programming language/examples",
  "std": "C:/Users/User/Desktop/programming language/lang/stdlib/lib"
}

path = "C:/Users/User/Desktop/programming language/examples/test_0.0.1.br"

resolver = Resolver(aliases)
resolver.resolve_modules(path)
modules = resolver.sort_modules()
interpreter = Interpreter(resolver)
interpreter.load_modules(modules)
interpreter.register_builtins(builtins)
interpreter.execute()
