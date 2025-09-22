import builtin.modules.types as types
import builtin.modules.console as console

# compose list of all builtin declarations
builtins = [
  *types.declarations,
  *console.declarations,
]
