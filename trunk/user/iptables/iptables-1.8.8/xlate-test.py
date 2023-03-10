#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import shlex
import argparse
from subprocess import Popen, PIPE

keywords = ("iptables-translate", "ip6tables-translate", "ebtables-translate")
xtables_nft_multi = 'xtables-nft-multi'

if sys.stdout.isatty():
    colors = {"magenta": "\033[95m", "green": "\033[92m", "yellow": "\033[93m",
              "red": "\033[91m", "end": "\033[0m"}
else:
    colors = {"magenta": "", "green": "", "yellow": "", "red": "", "end": ""}


def magenta(string):
    return colors["magenta"] + string + colors["end"]


def red(string):
    return colors["red"] + string + colors["end"]


def yellow(string):
    return colors["yellow"] + string + colors["end"]


def green(string):
    return colors["green"] + string + colors["end"]


def run_test(name, payload):
    global xtables_nft_multi
    test_passed = True
    tests = passed = failed = errors = 0
    result = []

    line = payload.readline()
    while line:
        if line.startswith(keywords):
            sourceline = line
            tests += 1
            process = Popen([ xtables_nft_multi ] + shlex.split(line), stdout=PIPE, stderr=PIPE)
            (output, error) = process.communicate()
            if process.returncode == 0:
                translation = output.decode("utf-8").rstrip(" \n")
                expected = payload.readline().rstrip(" \n")
                next_expected = payload.readline()
                if next_expected.startswith("nft"):
                    expected += "\n" + next_expected.rstrip(" \n")
                    line = payload.readline()
                else:
                    line = next_expected
                if translation != expected:
                    test_passed = False
                    failed += 1
                    result.append(name + ": " + red("Fail"))
                    result.append(magenta("src: ") + sourceline.rstrip(" \n"))
                    result.append(magenta("exp: ") + expected)
                    result.append(magenta("res: ") + translation + "\n")
                else:
                    passed += 1
            else:
                test_passed = False
                errors += 1
                result.append(name + ": " + red("Error: ") + "iptables-translate failure")
                result.append(error.decode("utf-8"))
                line = payload.readline()
        else:
                line = payload.readline()
    if (passed == tests) and not args.test:
        print(name + ": " + green("OK"))
    if not test_passed:
        print("\n".join(result), file=sys.stderr)
    return tests, passed, failed, errors


def load_test_files():
    test_files = total_tests = total_passed = total_error = total_failed = 0
    tests = sorted(os.listdir("extensions"))
    for test in ['extensions/' + f for f in tests if f.endswith(".txlate")]:
        with open(test, "r") as payload:
            tests, passed, failed, errors = run_test(test, payload)
            test_files += 1
            total_tests += tests
            total_passed += passed
            total_failed += failed
            total_error += errors
    return (test_files, total_tests, total_passed, total_failed, total_error)


def main():
    global xtables_nft_multi
    if not args.host:
        os.putenv("XTABLES_LIBDIR", os.path.abspath("extensions"))
        xtables_nft_multi = os.path.abspath(os.path.curdir) \
                            + '/iptables/' + xtables_nft_multi

    files = tests = passed = failed = errors = 0
    if args.test:
        if not args.test.endswith(".txlate"):
            args.test += ".txlate"
        try:
            with open(args.test, "r") as payload:
                files = 1
                tests, passed, failed, errors = run_test(args.test, payload)
        except IOError:
            print(red("Error: ") + "test file does not exist", file=sys.stderr)
            return -1
    else:
        files, tests, passed, failed, errors = load_test_files()

    if files > 1:
        file_word = "files"
    else:
        file_word = "file"
    print("%d test %s, %d tests, %d tests passed, %d tests failed, %d errors"
            % (files, file_word, tests, passed, failed, errors))
    return passed - tests


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', action='store_true',
                    help='Run tests against installed binaries')
parser.add_argument("test", nargs="?", help="run only the specified test file")
args = parser.parse_args()
sys.exit(main())
