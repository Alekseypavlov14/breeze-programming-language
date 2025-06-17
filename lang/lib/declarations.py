from parser.types.node import *
from parser.types.expressions import *

# represents externally defined node of AST
# has to be used for declarations in python modules
# all external declarations instantiate from this class
# external declarations are executed by INTERPRETER
# external declarations base on PARSER node/expression/statement if possible
class ExternalDeclaration(Node):
  pass

# represents constant declaration
class ExternalConstantDeclaration(ExternalDeclaration):
  def __init__(self, name: str, value):
    super().__init__()

    self.name = name
    self.value = value

# represents function declaration
class ExternalFunctionDeclaration(ExternalDeclaration):
  def __init__(self, name: str, parameters: list[FunctionParameterExpression], callable):
    super().__init__()

    self.name = name
    self.parameters = parameters
    self.callable = callable

# represents object declaration
# obj is a dict from KEY (str | number) to ANY value 
class ExternalObjectDeclaration(ExternalDeclaration):
  def __init__(self, name: str, obj: dict):
    super().__init__()

    self.name = name
    self.obj = obj


def is_declaration_of_type(declaration, *types: ExternalDeclaration):
  return isinstance(declaration, *types)
