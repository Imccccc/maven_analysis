#!/usr/bin/python3 

import os
import sys
import argparse
import subprocess
from loguru import logger

# constant variables
MVN_ANALYZE_DIR = 'maven_dependency_list'
REPORT_DIR = 'report'
ALL_DEPENDENCY_FILE = 'all_dependency_report'
MOBIKE_DEPENDENCY_FILE = 'mobike_dependency_report'
# global variables
out_path = '/tmp'
# stat
all_dir_count = 0
failed_dir_count = 0 # 没有处理成功的
failed_dir_list = []


def has_pom(path):
    ret = set(os.listdir(path))
    return "pom.xml" in ret


def is_mobike_dependnecy(dependency):
    ismbd = dependency.startswith('com.mobike') or 'bike' in dependency
    if ismbd:
        logger.debug('{} is mobike dependency', dependency)
    else:
        logger.debug('{} is not mobike dependency', dependency)
    return 


def get_all_dir_contains_pom(path):
    '''
    return all maven proejct in current path
    '''
    ret_dir = []
    for root, directory, files in os.walk(path):
        for dir in directory:
            full_path = os.path.join(root, dir)
            if has_pom(full_path):
                ret_dir.append({'path': full_path, 'dirname': dir})
        break
    return ret_dir


def get_all_analyze_report():
    from_dir = os.path.join(out_path, MVN_ANALYZE_DIR)

    for root, _, files in os.walk(from_dir):
        return [{'name': file, 'path': os.path.join(root, file)} for file in files]


def analyze_dependency():
    '''
    检查之前mvn生成的所有文件 然后分类输出一下
    '''
    all_dependency_set = set()
    file_entries_list = get_all_analyze_report()
    for file_entry in file_entries_list:
        with open(file_entry['path']) as read_fp:
            next(read_fp)
            for line in read_fp:
                all_dependency_set.add(line.strip())
    return generate_report(all_dependency_set, is_mobike_dependnecy)


def generate_report(dependency_set, filter):
    all_dep_count = 0
    mb_dep_count = 0
    all_dep_out_path = os.path.join(out_path, REPORT_DIR, ALL_DEPENDENCY_FILE)
    mobike_dep_out_path = os.path.join(
        out_path, REPORT_DIR, MOBIKE_DEPENDENCY_FILE)
    with open(all_dep_out_path, 'w') as all_dep_fp, open(mobike_dep_out_path, 'w') as mb_dep_fp:
        for dependency in dependency_set:
            if filter(dependency):
                mb_dep_fp.write(dependency + '\n')
                mb_dep_count += 1
            all_dep_fp.write(dependency + '\n')
            all_dep_count += 1
    logger.info('found {} of {} mobike dependencies', mb_dep_count, all_dep_count)
    return all_dep_count, mb_dep_count


def get_all_file(path):
    ret_dir = []
    for root, directory, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            ret_dir.append(file)
        break
    return ret_dir
        

def run_entry(path, outpath):
    global all_dir_count
    
    all_mvn_path = get_all_dir_contains_pom(path)
    all_dir_count = len(all_mvn_path)
    logger.info("found {} projects", all_dir_count)
    logger.info("projects are {}", all_mvn_path)
    for curr in all_mvn_path:
        logger.info("current we are handling {}", curr['dirname'])
        execute_in_dir(curr)
    # we get all dependency in out_path/MVN_ANALYZE_DIR
    analyze_dependency()

    logger.info('processed {} project, {} failed', all_dir_count, failed_dir_count)
    if failed_dir_count > 0:
        logger.error("failed projects are {}", failed_dir_list)


def execute_in_dir(entry):
    global failed_dir_count
    global failed_dir_list
    os.chdir(entry['path'])
    output_file = os.path.join(out_path, MVN_ANALYZE_DIR, entry['dirname'])
    logger.debug('maven output file at {}', output_file)
    this_out = subprocess.call(
        ['mvn', 'dependency:list', '-DoutputFile=' + output_file])
    logger.info(this_out)
    if this_out != 0:
        failed_dir_count += 1
        failed_dir_list.append(entry)


def check_dir():
    for dir in [MVN_ANALYZE_DIR, REPORT_DIR]:
        path = os.path.join(out_path, dir)
        if not os.path.exists(path):
            logger.info('path: {} not exist', path)
            os.makedirs(path)


def main(arguments):
    global out_path
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help="the path to all maven projects")
    parser.add_argument('-o', '--outpath', help="Output path default \"/tmp\" ", default="/tmp")
    # type=argparse.FileType('w')

    args = parser.parse_args(arguments)
    logger.info(args)
    out_path = out_path
    check_dir()
    run_entry(args.path, args.outpath)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

