import stdlib.builtin.modules.types as types
import stdlib.builtin.modules.console as console

# compose list of all builtin declarations
builtins = [
  *types.declarations,
  *console.declarations,
]
