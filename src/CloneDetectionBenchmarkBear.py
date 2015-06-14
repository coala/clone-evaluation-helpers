import re
from matplotlib import pyplot as plt
import numpy as np

from coalib.bears.GlobalBear import GlobalBear
from bears.codeclone_detection.ClangSimilarityBear import ClangSimilarityBear


class CloneDetectionBenchmarkBear(GlobalBear):
    def run(self,
            dependency_results: dict,
            clones: str=".*\/clones.*"):
        '''
        Checks the quality of the code clone detection on the given test files.

        :param clones:     A regex matching paths of files that contain known
                           clones. All others are considered non-clones.
        '''
        differences = dependency_results["ClangSimilarityBear"][0].contents

        clones_diffs = [0]
        non_clones_diffs = [1]

        seen_functions = []
        for function_1, function_2, difference in differences:
            if function_1[0] not in seen_functions:
                seen_functions.append(function_1[0])
            if function_2[0] not in seen_functions:
                seen_functions.append(function_2[0])

            if function_1[0] != function_2[0]:
                continue

            if re.match(clones, function_1[0]) is not None:
                clones_diffs.append(difference)
            else:
                non_clones_diffs.append(difference)

        print("\n".join(seen_functions))

        self.warn(" CD:", str(clones_diffs))
        self.warn("NCD:", str(non_clones_diffs))

        self.warn("Maximum clone difference:", str(max(clones_diffs)))
        self.warn("Minimum non-clone difference:", str(min(non_clones_diffs)))
        if max(clones_diffs) > min(non_clones_diffs):
            self.err("Code clone detection failed!")

        plt.xlim(0, 1)
        plt.ylim(0.5, 1.5)

        y = np.ones(np.shape(clones_diffs))
        plt.plot(clones_diffs, y, '|', ms=40, color='r', label="Clones")
        y = np.ones(np.shape(non_clones_diffs))
        plt.plot(non_clones_diffs, y, '|', ms=40, color='g',
                 label="Non-Clones")
        plt.grid()
        plt.show()

    @staticmethod
    def get_dependencies():
        return [ClangSimilarityBear]
