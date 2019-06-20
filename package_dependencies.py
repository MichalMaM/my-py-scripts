#!/usr/bin/env python3
import os
import json
import shutil
import sys
from itertools import chain
from optparse import OptionParser


def parse_options():
    usage = "usage: %prog [options] my_package_json foreign_package_json"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dev", dest="dev", action="store_true",
                      help="Use devDependencies instead of dependencies")
    parser.add_option("-m", "--my-foreign-sync", dest="my_foreign_sync", action="store_true",
                      help="Print my packages and same packages with versions sync with foreign")
    parser.add_option("-f", "--foreign-my-sync", dest="foreign_my_sync", action="store_true",
                      help="Print foreign packages and same packages with versions sync with my")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")
    return args, options

def parse_json_file(file_name):
    with open(file_name, 'r') as ifile:
        print("Read %s file" % file_name)
        return json.load(ifile)

def print_my_plus_same_sync_with_foreign(dependencies, diffs):
    data = sorted(chain(diffs["only_in_my"], diffs["in_both"]))
    for ind, i in enumerate(data):
        source = dependencies["foreign"] if i in diffs["in_both"] else dependencies["my"]
        comma = "" if ind == len(data) - 1 else ","
        print('\033[94m"%s": "%s"%s\033[0m' % (i, source[i], comma))

def print_foreign_plus_same_sync_with_my(dependencies, diffs):
    data = sorted(chain(diffs["only_in_foreign"], diffs["in_both"]))
    for ind, i in enumerate(data):
        source = dependencies["my"] if i in diffs["in_both"] else dependencies["foreign"]
        comma = "" if ind == len(data) - 1 else ","
        print('\033[94m"%s": "%s"%s\033[0m' % (i, source[i], comma))

def print_diff(dependencies, diffs):
    for i in sorted(diffs["in_both_with_diff_version"]):
        print('\033[0m"%s": \033[92m"%s" \033[0m-> \033[91m"%s"\033[0m,' % (
            i, dependencies["my"][i], dependencies["foreign"][i])
        )
    for i in sorted(diffs["only_in_my"]):
        print('\033[92m"%s": "%s"\033[0m,' % (i, dependencies["my"][i]))
    for i in sorted(diffs["only_in_foreign"]):
        print('\033[91m"%s": "%s"\033[0m,' % (i, dependencies["foreign"][i]))

def run(args, options):
    my_package_json = args[0]
    foreign_package_json = args[1]
    dependencies_key = "devDependencies" if options.dev else "dependencies"
    my_package_obj = parse_json_file(my_package_json)
    foreign_package_obj = parse_json_file(foreign_package_json)
    my_package_dependencies = my_package_obj[dependencies_key] or {}
    foreign_package_dependencies = foreign_package_obj[dependencies_key] or {}
    my_package_dependencies_set = set(my_package_dependencies.keys())
    foreign_package_dependencies_set = set(foreign_package_dependencies.keys())
    dependencies = {"my": my_package_dependencies, "foreign": foreign_package_dependencies}
    diffs = {
        "only_in_my": my_package_dependencies_set - foreign_package_dependencies_set,
        "only_in_foreign": foreign_package_dependencies_set - my_package_dependencies_set,
        "in_both": my_package_dependencies_set & foreign_package_dependencies_set,
        "in_both_with_diff_version": {i for i in my_package_dependencies_set & foreign_package_dependencies_set
                                        if my_package_dependencies[i] != foreign_package_dependencies[i]}
    }

    if options.my_foreign_sync:
        print_my_plus_same_sync_with_foreign(dependencies, diffs)
    elif options.foreign_my_sync:
        print_foreign_plus_same_sync_with_my(dependencies, diffs)
    else:
        print_diff(dependencies, diffs)



def main():
    run(*parse_options())


if __name__ == "__main__":
    main()
