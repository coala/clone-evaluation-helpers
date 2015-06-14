import os
from collections import OrderedDict
from queue import Queue
import re

from bears.codeclone_detection.ClangSimilarityBear import (
    counting_condition_dict,
    ClangSimilarityBear)
from coalib.collecting.Collectors import collect_files
from coalib.misc.StringConverter import StringConverter
from coalib.output.printers.ConsolePrinter import ConsolePrinter
from coalib.processes.Processing import get_file_dict
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting

condition_dict = counting_condition_dict(StringConverter(
    "returned,"
    "is_condition,"
    "in_condition,"
    "in_second_level_condition,"
    "in_third_level_condition,"
    "is_assignee,"
    "is_assigner,"
    "loop_content,"
    "second_level_loop_content,"
    "third_level_loop_content,"
    "is_param,"
    "in_sum,"
    "in_product,"
    "in_binary_operation,"
    "member_accessed,"
    "is_called,"
    "is_call_param"))

#weighting_range = [1, 0, 0.2, 0.4, 0.6, 0.8, 1.2, 1.4, 1.6, 1.8, 2]
weighting_range = [1, 0.8, 0.6, 0.4, 0.2, 0, 1.2, 1.4, 1.6, 1.8, 2]

section = Section("default")
section.append(Setting("files",
                       "../coala/bears/tests/codeclone_detection"
                       "/clone_detection_samples/**/*.c",
                       origin=os.path.abspath(
    "../coala/bears/tests/codeclone_detection/clone_detection_samples/")))
log_printer = ConsolePrinter()
filename_list = collect_files(['/home/lasse/prog/coala/bears/tests/codeclone_detection/clone_detection_samples/**/*.c'], log_printer)
file_dict = get_file_dict(filename_list, log_printer)

sorted_dict = OrderedDict(reversed(sorted(condition_dict.items(),
                                 key=lambda f: f[0].__name__)))
message_queue = Queue()


def fitness(c_dict):
    differences = ClangSimilarityBear(file_dict, section, message_queue).run(
        c_dict)[0].contents

    clones_diffs = [0]
    non_clones_diffs = [1]
    clones=".*\/clones.*"
    for function_1, function_2, difference in differences:
            if function_1[0] != function_2[0]:
                continue

            if re.match(clones, function_1[0]) is not None:
                clones_diffs.append(difference)
            else:
                non_clones_diffs.append(difference)

    return min(non_clones_diffs) - max(clones_diffs)


def optimize_key(c_dict, key, old_fitness):
    best = (1, old_fitness)
    for weighting in weighting_range:
        print("Checking", key.__name__, "with", weighting, "...")
        c_dict[key] = weighting
        fit = fitness(c_dict)
        if fit > best[1]:
            print("Better fitness found:", fit)
            best = weighting, fit

    c_dict[key] = best[0]
    return best[1]


if __name__ == '__main__':
    new_fitness = 0
    for key in sorted_dict.keys():
        new_fitness = optimize_key(sorted_dict, key, new_fitness)
        print("Weightings are:")
        for key in sorted_dict.keys():
            print("  ", key.__name__+":", str(sorted_dict[key])+",")

    print("\n\nFINISHED.\n\n")
    print("Got fitness:", new_fitness)
    print("Weightings are:")
    for key in sorted_dict.keys():
        print("  ", key.__name__+":", str(sorted_dict[key])+",")
