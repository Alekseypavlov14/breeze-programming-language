from parser.types.statements import BlockStatement

# this class represents independent module of the app
# modules are files

# path - path to the module (can be used as ID)
# content - parsed AST of the module
# dependencies - modules that the current module depend on
class Module:
  def __init__(self, path: str, content: BlockStatement, dependencies: list["Module"] = []):
    self.path = path
    self.content = content
    self.dependencies = dependencies
