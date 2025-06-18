from lexer.lexer import Lexer
from parser.parser import Parser
from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

# THIS CODE IS TEST

aliases = {
  "base": "C:/Users/User/Desktop/programming language/examples",
  "std": "C:/Users/User/Desktop/programming language/lang/lib/modules"
}

path = "C:/Users/User/Desktop/programming language/examples/test_0.0.1.br"

resolver = Resolver(aliases)
resolver.resolve_modules(path)
modules = resolver.sort_modules()
interpreter = Interpreter(resolver)
interpreter.load_modules(modules)
interpreter.execute()

print(interpreter.stacks[1].get_container_by_name('d').read())