from coalib.bears.LocalBear import LocalBear
from coalib.bearlib.parsing.clang.cindex import Index


class ClangASTPrintBear(LocalBear):
    def print_node(self, cursor, before="", spec_before=""):
        """
        Prints this node and all child nodes recursively in the style of:

        -node
        |-child
        `-another child
         |-child of child
         `-last child of child

        :param cursor:      The node to print. (Clang cursor.)
        :param before:      What to print before the node.
        :param spec_before: What to print before this node but to replace with
                            spaces for child nodes.
        """
        print(before + spec_before + "-",
              str(cursor.displayname.decode()),
              str(cursor.kind),
              str(cursor.location.line))

        children = list(cursor.get_children())

        if len(children) > 0:
            for child in children[:-1]:
                self.print_node(child, before + len(spec_before)*" " + "|")

            self.print_node(children[-1], before + len(spec_before)*" ", "`")

    def run(self,
            filename,
            file):
        """
        This bear is meant for debugging purposes relating to clang. It just
        prints out the whole AST for a file.
        """
        root = Index.create().parse(filename).cursor

        self.print_node(root)
