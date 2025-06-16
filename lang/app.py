from lexer.lexer import Lexer
from parser.parser import Parser
from resolution.resolver import Resolver
from interpreter.interpreter import Interpreter

# THIS CODE IS TEST

resolver = Resolver()

path = "C:/Users/User/Desktop/programming language/examples/test_0.0.1.br"
resolver.resolve_modules(path)

content = resolver.get_module_content_by_absolute_path(path)

lexer = Lexer()
parser = Parser()

st = parser.parse(lexer.parse(content))
print(st.statements)

modules = resolver.sort_modules()
for module in modules:
  print(f"Module with path: {module.path}")
  for statement in module.content.statements:
    print(statement)

interpreter = Interpreter()
interpreter.load_modules(modules)
interpreter.execute()
