# Breeze - general purpose programming language

## Description

Breeze is a general-purpose interpretable programming language. It has a developed standard library and well-looking syntax that is familiar to JavaScript syntax.

## Syntax

### Variables and Constants 

To declare a variable, there is a keyword ```var```. Example:
```js
var num = 10
```

To declare a constant, the keyword ```const``` is applied:
```js
var num = 10
```

### Control Flow

Conditions:

```js
if (value < 10) {
  console.output("Less than 10")
} else {
  console.output("Greater or equal to 10")
}
```

For loop:
```js
for (var i = 0; i < 10; i++) {
  console.output("Iteration")
}
```

While loop:
```js
var i = 0
while (i < 10) {
  console.output("Iteration")
  i++
}
```

```break``` and ```continue``` keywords work similarly to JavaScript.

### Function declarations

```js
function greet(name) {
  console.output("Hello " + name)
}

function sum(a, b) {
  return a + b
}
```

### Imports and Exports

```js
import { console } from "@std/console"

export const name = "Alex"
```
