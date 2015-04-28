from bears.codeclone_detection.CountVector import CountVector
from munkres import Munkres


def similarity(cv1, cv2):
    assert isinstance(cv1, CountVector)
    assert isinstance(cv2, CountVector)

    raise NotImplementedError


def find_max_match(cm1, cm2):
    cost_matrix = []

    for cv1 in cm1:
        nxt = []
        cost_matrix.append(nxt)
        for cv2 in cm2:
            nxt.append(similarity(cv1, cv2))

    matched = Munkres().compute(cost_matrix)
    # TODO: Create similarity value for the functions
    raise NotImplementedError
