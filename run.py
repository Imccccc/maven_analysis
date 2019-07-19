#!/usr/bin/python3 

from __future__ import print_function
import os
import sys
import argparse
from loguru import logger


def has_pom(path):
    ret = set(os.listdir(path))
    return "pom.xml" in ret



def get_all_dir_contains_pom(path):
    '''
    return all maven proejct in current path
    '''
    ret_dir = []
    for root, directory, files in os.walk(path):
        for dir in directory:
            full_path = os.path.join(root, dir)
            if has_pom(full_path):
                ret_dir.append(full_path)
        break
    return ret_dir


def get_all_file(path):
    ret_dir = []
    for root, directory, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            ret_dir.append(file)
        break
    return ret_dir
        


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help="the path to all maven projects")
    parser.add_argument('-o', '--outpath', help="Output path", default=None)
    # type=argparse.FileType('w')

    args = parser.parse_args(arguments)
    logger.info(args)
    run_entry(args.path, args.outpath)


def run_entry(path, outpath):
    all_mvn_path = get_all_dir_contains_pom(path)
    logger.info("found {} projects", len(all_mvn_path))
    logger.info("projects are {}", all_mvn_path)
    for curr in all_mvn_path:
        logger.info("current we are handling {}", curr)



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

