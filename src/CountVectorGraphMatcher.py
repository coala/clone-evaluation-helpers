from bears.codeclone_detection.CountVector import CountVector
from math import sqrt
from munkres import Munkres
# Instantiate globally since this class is holding stateless public methods.
munkres = Munkres()


def difference(cv1, cv2):
    """
    Compares the variables represented by the given count vectors.

    :param cv1: A CountVector object representing the first function.
    :param cv2: A CountVector object representing the second function.
    :return:    A difference value between 0 (identical) and 1 (not similar).
    """
    assert isinstance(cv1, CountVector)
    assert isinstance(cv2, CountVector)
    assert len(cv1) == len(cv2)

    # Return distance normalized by the longer vector
    return sqrt(sum((ce1 - ce2)**2
                    for ce1, ce2 in zip(cv1, cv2)))/max(abs(cv1), abs(cv2))


def compare_functions(cm1, cm2):
    """
    Compares the functions represented by the given count matrices.

    :param cm1: Count matrix for the first function.
    :param cm2: Count matrix for the second function.
    :return:    The difference between these functions, 0 is identical and 1
                is not similar at all.
    """
    # The cost matrix holds the difference between the two variables i and j
    # in the i/j field. This is a representation of a bipartite weighted graph
    # with nodes representing the first function on the one side (rows) and the
    # nodes representing the second function on the other side (columns). The
    # fields in the matrix are the weighted nodes connecting each element from
    # one side to the other.
    cost_matrix = [[difference(cv1, cv2)
                    for cv2 in cm2]
                   for cv1 in cm1]

    # Pad manually, we'll access the zeros when iterating over matching, this
    # will thus make the matrix square and thus a legal input for munkres while
    # the zeros don't change the result. They are simply put dummy variables
    # which don't influence the result.
    cost_matrix = munkres.pad_matrix(cost_matrix)

    # The munkres algorithm will calculate a matching such that the sum of the
    # taken fields is minimal. It thus will associate each variable from one
    # function to one on the other function.
    matching = munkres.compute(cost_matrix)

    # Sum it up, normalize it so we have a value in [0, 1]
    return sum(cost_matrix[x][y] for x, y in matching)/len(matching)
