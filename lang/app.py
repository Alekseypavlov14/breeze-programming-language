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
  Hello = 0
}
{
  Block = 9
  {
    Nested = 0
    hello = "ABC \n DEF"
  }
}
"""
list2 = lexer.parse_module(code2)
for token in list2:
  print(token)

block = parser.parse(lexer.parse_module(code2))
for statements in block.statements:
  print(statements)
