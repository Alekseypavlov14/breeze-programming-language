from resolution.module import *

# this class is used to contain application modules (files)
# it provides utils for topological sort based on dependencies
class Registry:
  def __init__(self):
    self.modules: list[Module] = []

  # adds new module to storage if it was NOT added earlier
  def add_module(self, module: Module):
    pass

  # checks if module by ABSOLUTE path is already added to prevent duplicates
  def is_module_added_by_path(self, path: str):
    pass

  # returns stored module by its ABSOLUTE path
  def get_module_by_absolute_path(self, path: str):
    pass

  # returns list of modules
  def get_modules(self) -> list[Module]:
    pass

  # sorts modules topologically in place
  def sort_topologically(self):
    pass
