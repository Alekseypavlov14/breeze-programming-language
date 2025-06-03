from resolution.module import *

# this class is used to contain application modules (files)
# it provides utils for topological sort based on dependencies
class Registry:
  def __init__(self):
    self.modules: list[Module] = []

  # adds new module to storage if it was NOT added earlier
  # add modules with computed dependencies list
  def add_module(self, module: Module):
    # do not add module if it is already added
    # absolute path is identifier
    if self.is_module_added_by_path(module.path):
      return
    
    # append module
    self.modules.append(module)

  # checks if module by ABSOLUTE path is already added to prevent duplicates
  def is_module_added_by_path(self, path: str):
    # search module with similar path
    for module in self.modules:
      if module.path == path:
        return True
      
    return False

  # returns stored module by its ABSOLUTE path
  # returns None if file is not found
  def get_module_by_absolute_path(self, path: str) -> Module | None:
    # search for module by path
    for module in self.modules:
      if module.path == path:
        return module
      
    # fallback      
    return None

  # returns list of modules
  def get_modules(self) -> list[Module]:
    return self.modules

  # sorts modules topologically in place
  def sort_topologically(self):
    pass
