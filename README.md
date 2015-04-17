# What is This?

This repository is a development repository for count matrix based code clone
detection for coala.

See
http://www.callowbird.com/uploads/8/6/6/4/8664563/cmcd_count_matrix_based_code_clone_detection.pdf

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
 * Create a variable data structure (i.e. object) holding
   * Definition information
   * Name
   * Counts under different conditions

## TODO until April 26:

 * Introduce Counting Conditions (dynamically, via function objects)
 * Cleanup
 * Write unittests

## TODO until May 10:

 * Undefined other tasks