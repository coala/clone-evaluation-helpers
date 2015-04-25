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
    # In every case the first child of IF_STMT is the condition itself
    # (non-NULL)
    return is_nth_child_of_kind(stack, [0], ci.CursorKind.IF_STMT)


def is_in_condition(cursor, stack):
    # In every case the first child of IF_STMT is the condition itself
    # (non-NULL) so the second and third child are in the then/else branch
    return is_nth_child_of_kind(stack, [1, 2], ci.CursorKind.IF_STMT)


arith_binary_operators = ['+', '-', '*', '/', '&', '|']
comparision_operators = ["==", "<=", ">=", "<", ">", "!="]
adv_assignment_operators = [op + "=" for op in arith_binary_operators]
assignment_operators = ["="] + adv_assignment_operators


def is_in_comparision(cursor, stack):
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.BINARY_OPERATOR:
            for token in elem.get_tokens():
                if token.spelling.decode() in comparision_operators:
                    return True

    return False


def is_in_assignment(cursor, stack):
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.BINARY_OPERATOR:
            for token in elem.get_tokens():
                if token.spelling.decode() in assignment_operators:
                    return True

    return False


def is_assignee(cursor, stack):
    cursor_end_pos = cursor.extent.end.line, cursor.extent.end.column
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.BINARY_OPERATOR:
            for token in elem.get_tokens():
                token_begin_pos = (token.extent.start.line,
                                   token.extent.start.column)
                # This needs to be an assignment and cursor has to be on LHS
                if (
                        token.spelling.decode() in assignment_operators and
                        cursor_end_pos <= token_begin_pos):
                    return True

    return False


def used_for_assignment(cursor, stack):
    # TODO count unary ops like ++/--
    cursor_beg_pos = cursor.extent.start.line, cursor.extent.start.column
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.BINARY_OPERATOR:
            for token in elem.get_tokens():
                token_end_pos = (token.extent.end.line,
                                   token.extent.end.column)
                # This needs to be an assignment and cursor has to be on LHS
                # or if we have something like += its irrelevant on which side
                # it is because += reads on both sides
                if (
                        token.spelling.decode() in assignment_operators and (
                            token_end_pos <= cursor_beg_pos or
                            token.spelling.decode != "=")):
                    return True

    return False


def get_position_in_for_loop(cursor, stack):
    # Yes, this is a very very dirty state machine
    count_position = True
    position = 0
    brackets = 0
    cursor_end_pos = cursor.extent.end.line, cursor.extent.end.column
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.FOR_STMT:
            for token in elem.get_tokens():
                token_begin_pos = (token.extent.start.line,
                                   token.extent.start.column)
                if count_position:
                    if token.spelling.decode() == ";":
                        if cursor_end_pos <= token_begin_pos:
                            return position

                        position += 1
                        if position > 1:
                            count_position = False
                else:
                    if token.spelling.decode() == "(":
                        brackets += 1
                    elif token.spelling.decode() == ")":
                        if brackets == 0:
                            if cursor_end_pos <= token_begin_pos:
                                return position
                            else:
                                return position + 1
                        else:
                            brackets -= 1

    return None


def is_for_declaration(cursor, stack):
    return get_position_in_for_loop(cursor, stack) is 0


def is_for_condition(cursor, stack):
    return get_position_in_for_loop(cursor, stack) is 1


def is_for_incrementor(cursor, stack):
    return get_position_in_for_loop(cursor, stack) is 2


def is_for_content(cursor, stack):
    return get_position_in_for_loop(cursor, stack) is 3


condition_dict = {"use": no_condition,
                  "in_if": is_in_condition,
                  "is_condition": is_condition,
                  "is_returned": is_returned,
                  "is_call_arg": is_call_argument,
                  "in_comparision": is_in_comparision,
                  "in_assignment": is_in_assignment,
                  "is_assignee": is_assignee,
                  "used_for_assignment": used_for_assignment,
                  "is_for_declaration": is_for_declaration,
                  "is_for_condition": is_for_condition,
                  "is_for_incrementor": is_for_incrementor,
                  "is_for_content": is_for_content}


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
                               is_call_arg, in_comparision, in_assignment,
                               is_assignee, used_for_assignment,
                               is_for_declaration, is_for_condition,
                               is_for_incrementor, is_for_content.
        """
        cc = ClangCountVectorCreator(conditions=condition_list)
        count_dict = cc.get_vectors_for_file(filename)
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
