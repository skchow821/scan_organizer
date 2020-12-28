import logging
import yaml
import argparse
import os
import shutil
import sys

def path_normalize(path):
    return os.path.abspath(os.path.expanduser(path))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Takes a yaml file as input to move files into directories based on filename and keyword matches.')
    parser.add_argument('--config', '-c', dest='config_file', required=True, help='config yaml for organization')
    parser.add_argument('--dry_run', action='store_true', help='Optional param for dry runs')
    arguments = parser.parse_args()
    arguments.config_file = path_normalize(arguments.config_file)
    return arguments

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, \
        format="%(asctime)s, %(module)s, %(funcName)s, %(message)s")


def validate_config(config):
    logging.debug("Contents {}".format(config))

    # required params are available
    required_keys = ["input_ext", "input_dir", "output_dir", "patterns"]
    for key in required_keys:
        if key not in config:
            logging.error("Config file must contain {}!".format(key))
            return None

    config["input_dir"] = path_normalize(config["input_dir"])
    config["output_dir"] = path_normalize(config["output_dir"])

    # normalize output directories
    for pair in config["patterns"]:
        pair["path"] = os.path.join(config["output_dir"], pair["path"])

    # create a list of directories to validate
    directories = [config["input_dir"]] + \
            [pair["path"] for pair in config["patterns"]]

    logging.debug("paths to validate: {}".format(directories))

    for directory in directories:
        if not os.path.isdir(directory):
            logging.error("Directory {} is not valid!".format(directory))
            return None

    return config

def main():
    setup_logging()
    args = parse_arguments()
    config_file = args.config_file
    if args.dry_run:
        logging.info("-- DRY RUN ONLY --")

    with open(args.config_file, 'r') as yaml_input:
        config = yaml.safe_load(yaml_input)
        config = validate_config(config)
        if config is None:
            sys.exit(1)

        for input_file in filter(lambda x : x.endswith(config["input_ext"]), \
                os.listdir(config["input_dir"])):
            for pattern in config["patterns"]:
                if pattern["terms"] in input_file:
                    src = os.path.join(config["input_dir"], input_file)
                    dest = pattern["path"]
                    logging.debug("mv {} {}".format(src, dest))

                    if not args.dry_run:
                        shutil.move(src, dest)
                    break

if __name__ == '__main__':
    main()
