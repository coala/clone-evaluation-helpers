from itertools import combinations
import multiprocessing
import re

from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection.ClangFunctionDifferenceBear import \
    counting_condition_dict, default_cc_dict, get_difference
from bears.codeclone_detection.CloneDetectionRoutines import get_count_matrices
from coalib.bears.GlobalBear import GlobalBear
from coalib.processes.Processing import get_cpu_count
import functools


def ret_diffs(count_matrices,
              average_calculation,
              poly_postprocessing,
              exp_postprocessing):
    f_combinations = [(f1, f2)
                      for f1, f2 in combinations(count_matrices, 2)]
    differences = []
    partial_get_difference = functools.partial(
        get_difference,
        count_matrices=count_matrices,
        average_calculation=average_calculation,
        poly_postprocessing=poly_postprocessing,
        exp_postprocessing=exp_postprocessing)
    for i, elem in enumerate(map(partial_get_difference, f_combinations)):
        differences.append(elem)

    return differences


def fitness(file_dict,
            conditions,
            weightings,
            clones,
            origin,
            average_calculation,
            poly_postprocessing,
            exp_postprocessing):
    differences = ret_diffs(get_count_matrices(
        ClangCountVectorCreator(conditions,
                                weightings),
        list(file_dict.keys()),
        lambda x: x,
        origin),
        average_calculation=average_calculation,
        poly_postprocessing=poly_postprocessing,
        exp_postprocessing=exp_postprocessing)

    clones_diffs = [0]
    non_clones_diffs = [1]

    must_have = list(file_dict.keys())
    for function_1, function_2, difference in differences:
        if function_1[0] != function_2[0]:
            continue

        if function_1[0] in must_have:
            must_have.remove(function_1[0])

        if re.match(clones, function_1[0]) is not None:
            clones_diffs.append(difference)
        else:
            non_clones_diffs.append(difference)

    for filename in must_have:
        if not re.match(clones, filename):
            must_have.remove(filename)

    # Each file must have one result yielded at least. If not some
    # function was ignored invalidly and that shouldn't be.
    return (min(non_clones_diffs) - max(clones_diffs) - len(must_have),
            max(clones_diffs))


def exchanged_fitness(weighting,
                      i,
                      file_dict,
                      conditions,
                      weightings,
                      clones,
                      origin,
                      average_calculation,
                      poly_postprocessing,
                      exp_postprocessing):
    tup = fitness(file_dict,
                  conditions,
                  weightings[:i]+[weighting]+weightings[i+1:],
                  clones,
                  origin,
                  average_calculation=average_calculation,
                  poly_postprocessing=poly_postprocessing,
                  exp_postprocessing=exp_postprocessing)
    return tup[0], tup[1], weighting


class ClangCCOptimizeBear(GlobalBear):
    def optimize_weighting(self,
                           conditions,
                           weightings,
                           clones,
                           i,
                           old_fitness,
                           mini,
                           average_calculation,
                           poly_postprocessing,
                           exp_postprocessing):
        self.debug("Optimizing condition", conditions[i].__name__, "...")
        best = (weightings[i], old_fitness)
        possible_weightings = [x/5 for x in range(11)]
        try:
            possible_weightings.remove(weightings[i])
        except ValueError:
            pass

        pool = multiprocessing.Pool(get_cpu_count())

        part_fitness = functools.partial(
            exchanged_fitness,
            i=i,
            weightings=weightings,
            file_dict=self.file_dict,
            origin=self.section["files"].origin,
            conditions=conditions,
            clones=clones,
            average_calculation=average_calculation,
            poly_postprocessing=poly_postprocessing,
            exp_postprocessing=exp_postprocessing)

        for fit, _mini, weighting in pool.imap(part_fitness,
                                               possible_weightings):
            if fit > best[1]:
                best = weighting, fit
                mini = _mini

        if weightings[i] != best[0]:
            self.debug("New fitness found:", best[1],
                       ", minimal threshold:", mini)
            self.warn("New value for {}: {}".format(
                conditions[i].__name__,
                best[0]))
            weightings[i] = best[0]
        return best[1]

    def optimize_weightings(self,
                            conditions,
                            initial_weightings,
                            clones,
                            average_calculation,
                            poly_postprocessing,
                            exp_postprocessing):
        fit, mini = fitness(self.file_dict,
                            conditions,
                            initial_weightings,
                            clones,
                            self.section["files"].origin,
                            average_calculation,
                            poly_postprocessing,
                            exp_postprocessing)
        self.debug("Initial fitness:", fit, ", minimal threshold:", mini)
        for i in range(len(initial_weightings)):
            fit = self.optimize_weighting(
                conditions,
                initial_weightings,
                clones,
                i,
                fit,
                mini,
                average_calculation=average_calculation,
                poly_postprocessing=poly_postprocessing,
                exp_postprocessing=exp_postprocessing)

        return initial_weightings

    def debug_weightings(self, conditions, weightings):
        for i in range(len(conditions)):
            self.debug("    {}: {},".format(
                conditions[i].__name__,
                weightings[i]))

    def run(self,
            counting_conditions: counting_condition_dict=default_cc_dict,
            clones: str=".*\/clones.*",
            average_calculation: bool=False,
            poly_postprocessing: bool=True,
            exp_postprocessing: bool=True):
        conditions = list(counting_conditions.keys())
        weightings = list(counting_conditions.values())

        self.debug("The following counting conditions and weightings will be "
                   "used as starting values:")
        self.debug_weightings(conditions, weightings)

        old = None
        while old != weightings:
            old = weightings.copy()
            weightings = self.optimize_weightings(
                conditions,
                weightings,
                clones,
                average_calculation=average_calculation,
                poly_postprocessing=poly_postprocessing,
                exp_postprocessing=exp_postprocessing)
            self.debug_weightings(conditions, weightings)
            if old != weightings:
                self.debug("Continuing investigation.")
