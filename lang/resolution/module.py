from parser.types.statements import BlockStatement

# this class represents independent module of the app
# source and external modules (lib) are instantiated from this class
# modules are files
class Module:
  def __init__(self, path: str, dependencies: list[str]):
    # absolute path of current module (ID)
    self.path = path
    # absolute paths to dependencies
    self.dependencies = dependencies

# content - parsed AST of the module (root statement)
class SourceModule(Module):
  def __init__(self, path: str, dependencies: list[str], content: BlockStatement):
    super().__init__(path, dependencies)

    self.content = content


def is_module_of_type(module: Module, *types: Module):
  return isinstance(module, *types)
