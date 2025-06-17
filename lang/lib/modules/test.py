from lib.module import ExternalModule

class TestModule(ExternalModule):
  def __init__(self, path):
    super().__init__(path, [], [])
    