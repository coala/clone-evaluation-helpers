# What is This?

This repository is a development repository for count matrix based code clone
detection for coala.

Note that this code is experimental and may not have unit tests. When it
becomes clean and generic enough it will be merged into the coala main
repository.

For more info about the algorithm, see
http://www.callowbird.com/uploads/8/6/6/4/8664563/cmcd_count_matrix_based_code_clone_detection.pdf

# Usage

Download and use coala on this project:

```
git clone https://github.com/coala-analyzer/coala
cd coala
sudo python3 setup.py install
cd ..
git clone https://github.com/coala-analyzer/clone-evaluation-helpers
cd clone-evaluation-helpers
coala
```
