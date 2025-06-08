from interpreter.stack import *
from resolution.module import *

# executes AST
class Interpreter:
  def __init__(self):
    # modules of application
    self.modules: list[Module] = []
    # list of stacks for each module
    self.stacks: list[Stack] = []

    # alias for current executing module
    # order of execution is defined by Resolver
    current_module: Module | None = None
    # alias for current stack
    # using imported functions requires switching the stack
    current_stack: Stack | None = None

  # method to load app modules to application
  # creates stack for each module
  def load_modules(self, modules: list[Module]):
    # set modules list
    self.modules = modules
    # create stacks for each module
    self.stacks = [Stack() for _ in modules]
