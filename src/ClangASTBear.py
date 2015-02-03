from coalib.bears.LocalBear import LocalBear
import clang.cindex


class ClangASTBear(LocalBear):
    def print_clang_cursor(self, cursor, indent=""):
        if cursor is None:
            return
        if len(indent) > 40:
            print("ABORTING")
            return

        self.debug_msg(indent + "Got child:")
        self.debug_msg(indent + "KIND:", cursor.kind)
        self.debug_msg(indent + "LOC :", cursor.location)

        for child in cursor.get_children():
            self.print_clang_cursor(child, indent+"| ")

    def run_bear(self, filename, file, *args):
        index = clang.cindex.Index.create()
        tree = index.parse(filename)
        self.debug_msg(str(tree.spelling))

        self.print_clang_cursor(tree.cursor)
