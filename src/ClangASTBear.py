from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from coalib.bearlib.parsing.clang import cindex as ci
from coalib.results.Result import Result


def no_condition(cursor, stack):
    return True


def is_call_argument(cursor, stack):
    for elem in stack:
        if elem.kind == ci.CursorKind.CALL_EXPR:
            return True

    return False


class ClangASTBear(LocalBear):
    def run(self, filename, file, *args):
        cc = ClangCountVectorCreator(conditions=[no_condition,
                                                 is_call_argument])
        count_dict = cc.get_vectors_for_file(filename)
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
