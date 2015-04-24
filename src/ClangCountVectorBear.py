from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from coalib.bearlib.parsing.clang import cindex as ci
from coalib.results.Result import Result
from coalib.settings.Setting import Setting


def no_condition(cursor, stack):
    return True


def stack_contains_kind(stack, kind):
    """
    Checks if a cursor with the given kind is within the stack.

    :param stack: The stack holding a tuple holding the parent cursors and the
                  child number.
    :param kind:  The kind of the cursor to search for.
    :return:      True if the kind was found.
    """
    for elem, child_num in stack:
        if elem.kind == kind:
            return True

    return False


def is_call_argument(cursor, stack):
    return stack_contains_kind(stack, ci.CursorKind.CALL_EXPR)


def is_returned(cursor, stack):
    return stack_contains_kind(stack, ci.CursorKind.RETURN_STMT)


def is_nth_child_of_kind(stack, allowed_nums, kind):
    """
    Checks if the stack contains a cursor with is of the given kind and the
    stack also has a child of this element which number is in the allowed_nums
    list.

    :param stack:        The stack holding a tuple holding the parent cursors
                         and the child number.
    :param allowed_nums: List/iterator of child numbers allowed.
    :param kind:         The kind of the parent element.
    :return:             True if the described situation matches.
    """
    is_kind_child = False
    for elem, child_num in stack:
        assert isinstance(elem, ci.Cursor)
        if is_kind_child and child_num in allowed_nums:
            return True

        if elem.kind == kind:
            is_kind_child = True
            print("IS WANTED KIND", kind)
            for token in elem.get_tokens():
                print("TK:", token.kind, ":", token.spelling.decode())
        else:
            is_kind_child = False

    return False


def is_condition(cursor, stack):
    return is_nth_child_of_kind(stack, [0], ci.CursorKind.IF_STMT)


def is_in_condition(cursor, stack):
    return is_nth_child_of_kind(stack, [1, 2], ci.CursorKind.IF_STMT)


condition_dict = {"use": no_condition,
                  "in_if": is_in_condition,
                  "is_condition": is_condition,
                  "is_returned": is_returned,
                  "is_call_arg": is_call_argument}


def cv_condition(value):
    """
    This is a custom converter to convert a setting from coala into counting
    condition function objects for this bear only.

    :param value: A Setting
    :return:      A list of functions (counting conditions)
    """
    assert isinstance(value, Setting)

    str_list = list(value)
    result_list = []
    for elem in str_list:
        result_list.append(condition_dict.get(elem.lower()))

    return result_list


class ClangCountVectorBear(LocalBear):
    def run(self,
            filename,
            file,
            condition_list: cv_condition):
        """
        Creates a count vector for each function in the given file(s).

        :param condition_list: A list of counting conditions. Possible values
                               are in_if, use, is_condition, is_returned,
                               is_call_arg.
        """
        cc = ClangCountVectorCreator(conditions=condition_list)
        count_dict = cc.get_vectors_for_file(filename)
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
