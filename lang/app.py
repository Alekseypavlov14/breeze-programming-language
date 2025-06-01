from lexer.lexer import Lexer
from parser.parser import Parser

# THIS CODE IS TEST

lexer = Lexer()
parser = Parser()

# TEST 1
# code = """
# function a() {}
# float a = 88.9
# string b = "hello"
# """
# list = lexer.parse_module(code)

# for token in list:
#   print(token)

# TEST 2
code2 = """
{
  Hello
}
{
  Block
  {
    Nested
    string hello = "ABC"
  }
}
"""
list2 = lexer.parse_module(code2)
for token in list2:
  print(token)

# print(parser.parse(lexer.parse_module(code2)))

