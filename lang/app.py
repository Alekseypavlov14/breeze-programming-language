from lexer.lexer import Lexer
from parser.parser import Parser
from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

# THIS CODE IS TEST

resolver = Resolver()

path = "C:/Users/User/Desktop/programming language/examples/test_0.0.1.br"
resolver.resolve_modules(path)
modules = resolver.sort_modules()
interpreter = Interpreter()
interpreter.load_modules(modules)
interpreter.execute()
