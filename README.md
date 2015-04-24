# What is This?

This repository is a development repository for count matrix based code clone
detection for coala. This code may make use off some code not yet merged into
coala so make sure you use the up to date version of it and checkout the
wip/sils/cc branch.

See
http://www.callowbird.com/uploads/8/6/6/4/8664563/cmcd_count_matrix_based_code_clone_detection.pdf

# Usage

Download and use coala on this project:

```
git clone https://github.com/coala-analyzer/coala
git checkout wip/sils/cc
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
 * Cleanup
 * Write unittests
 * Introduce Counting Conditions (dynamically, via function objects)
 * Let Counting Conditions be configured via coala

## TODO until April 26:

 * Introduce more Counting Conditions

## TODO until May 10:

 * Undefined other tasks
