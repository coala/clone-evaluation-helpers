from bears.codeclone_detection.CountVector import CountVector
from munkres import Munkres


def similarity(cv1, cv2):
    assert isinstance(cv1, CountVector)
    assert isinstance(cv2, CountVector)

    raise NotImplementedError


def find_max_match(cm1, cm2):
    cost_matrix = []

    for cv1 in cm1:
        cost_matrix.append([similarity(cv1, cv2) for cv2 in cm2])

    munkres = Munkres()
    # Pad manually, we'll access the zeros when iterating over matching
    cost_matrix = munkres.pad_matrix(cost_matrix)
    matching = munkres.compute(cost_matrix)

    cost_sum = sum(cost_matrix[x][y] for x, y in matching)

    # TODO: Create similarity value for the functions
    raise NotImplementedError
