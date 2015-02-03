from coalib.bears.LocalBear import LocalBear
import clang.cindex


class ClangASTBear(LocalBear):
    def run_bear(self, filename, file, *args):
        index = clang.cindex.Index.create()
        tree = index.parse(filename)
        self.debug_msg(str(tree.spelling))
