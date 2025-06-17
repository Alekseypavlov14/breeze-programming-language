from lib.declarations import *
from resolution.module import *

# all external modules define a class instantiated from this class
class ExternalModule(Module):
  def __init__(self, path: str, dependencies: list[str], declarations: list[ExternalDeclaration]):
    super().__init__(path, dependencies)

    # list of external declarations
    self.declarations = declarations
