from parser.types.statements import BlockStatement

# this class represents independent module of the app
# modules are files
class Module:
  def __init__(self, path: str, dependencies: list[str], content: BlockStatement):
    # absolute path of current module (ID)
    self.path = path
    # absolute paths to dependencies
    self.dependencies = dependencies
    # parsed AST of the module
    self.content = content
