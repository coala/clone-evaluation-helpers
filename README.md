# What is This?

This repository holds a bear that generates an AST for some languages via
clang.

# Usage

Download and use coala on this project:

```
git clone https://github.com/coala-analyzer/coala
cd coala
sudo python3 setup.py install
cd ..
git clone https://github.com/coala-analyzer/clang-ast-bear
cd clang-ast-bear
coala
```

# Status

## Done:

 * Getting clang to work
 * Print clang AST
 * Retrieve variable declarations
 * Count variable usages within functions

## TODO until April 26:

 * Create a variable data structure (i.e. object) holding
   * Definition information
   * Name
   * Counts under different conditions
 * Introduce Counting Conditions (dynamically, via function objects)
 * Cleanup
 * Write unittests

## TODO until May 10:

 * Undefined other tasks