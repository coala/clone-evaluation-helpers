from coalib.bears.LocalBear import LocalBear


class ClangASTBear(LocalBear):
    def run_bear(self, filename, file, *args):
        self.debug_msg(filename)
