# use for invalid path for dependencies
class PathError(Exception):
  def __init__(self, message: str):
    super().__init__(message)

# use when path leads to invalid module
class ModuleError(Exception):
  def __init__(self, message: str):
    super().__init__(message)
    
# use for resolution error (during topological sort)
class ResolutionError(Exception):
  def __init__(self, message: str):
    super().__init__(message)