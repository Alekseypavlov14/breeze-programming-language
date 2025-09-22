# root class for builtin declaration
class BuiltInDeclaration:
  pass

class ConstantBuiltInDeclaration(BuiltInDeclaration):
  def __init__(self, name: str, value):
    self.name = name
    self.value = value

class FunctionBuiltInDeclaration(BuiltInDeclaration):
  def __init__(self, name: str, arguments: int, callable):
    self.name = name
    self.arguments = arguments
    self.callable = callable


def is_declaration_of_type(declaration, *types: BuiltInDeclaration):
  return isinstance(declaration, *types)
