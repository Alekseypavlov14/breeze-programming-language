from lexer.lexer import Lexer
from parser.parser import Parser
from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

# THIS CODE IS TEST

aliases = {
  "base": "C:/Users/User/Desktop/programming language/examples"
}

path = "C:/Users/User/Desktop/programming language/examples/example1.br"

resolver = Resolver(aliases)
resolver.resolve_modules(path)
modules = resolver.sort_modules()
interpreter = Interpreter()
interpreter.load_modules(modules)
interpreter.execute()
