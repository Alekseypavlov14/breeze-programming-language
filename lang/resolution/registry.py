from resolution.module import *
from resolution.exceptions import *

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
    # search module with path
    return bool(self.get_module_by_absolute_path(path))

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
    # set of all module paths in registry
    undiscovered: set[str] = set(map(lambda module: module.path, self.modules))
    # set of module paths that are discovered but not analyzed
    discovered = set()
    # set of module paths that are analyzed 
    analyzed = set()

    # list of nodes in topologically sorted order
    sorted = []

    # DFS algorithm iteration (recursive)
    def depth_first_search(path: str):
      # if path is analyzed
      if path in analyzed:
        # do not analyze this module again
        return
      
      # if cycle is completed and depth-first search reached discovered node
      if path in discovered:
        raise ResolutionError(f'Circular dependency including module by path {path}')
      
      # discover node
      undiscovered.remove(path)
      discovered.add(path)
      
      # get module from current registry
      module: Module = self.get_module_by_absolute_path(path)
      if not module:
        raise ModuleError('Module was not accessible during topological sort')

      # discover all successors
      # dependencies are paths
      for dependency in module.dependencies:
        depth_first_search(dependency)

      # analyze node (all dependencies are analyzed)
      discovered.remove(path)
      analyzed.add(path)

      # add module to sorted
      sorted.append(module)

    # in_degree is needed to start DFS only from 0 in-degree nodes (requirement of algorithm)
    modules_in_degree: list[int] = []

    # compute in-degree for each module
    for module in self.modules:
      # compute in_degree
      in_degree = 0

      # analyze potential dependent modules
      for dependent in self.modules:
        # skip current module
        if dependent.path == module.path:
          continue
        
        # increment in_degree if needed
        if module.path in dependent.dependencies:
          in_degree += 1

      modules_in_degree.append(in_degree)

    # execute DFS
    for module_index in range(len(self.modules)):
      # check for zero in_degree
      if modules_in_degree[module_index] == 0: 
        # call DFS with PATH
        depth_first_search(self.modules[module_index].path)

    # check if DFS is executed
    # if registry contains modules but no module was analyzed and added to sorted
    # Indicates that every module has in-degree. It indicates Circular Dependency
    if len(self.modules) and not len(sorted):
      raise ResolutionError('Circular dependency in modules. Every module is dependent on others')

    # reverse list to have dependencies at the beginning and dependents at the end
    sorted.reverse()

    # update modules field with sorted modules
    self.modules = sorted

    return sorted
  