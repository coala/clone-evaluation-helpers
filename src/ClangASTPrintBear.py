from coalib.bears.LocalBear import LocalBear
from coalib.bearlib.parsing.clang.cindex import Index


class ClangASTPrintBear(LocalBear):
    def print_node(self, cursor, pre=""):
        print(pre + "-", str(cursor.kind))

        if pre[-1:] == "`":
            pre = pre[:-1] + " "

        children = list(cursor.get_children())

        if len(children) > 0:
            for child in children[:-1]:
                self.print_node(child, pre + "|")

            self.print_node(children[-1], pre + "`")

    def run(self,
            filename,
            file):
        """
        This bear is meant for debugging purposes relating to clang. It just
        prints out the whole AST for a file.
        """
        root = Index.create().parse(filename).cursor

        self.print_node(root)
