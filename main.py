#!/usr/bin/env python
import sys, argparse
import yaml
import logging
logging.getLogger().setLevel(logging.INFO)
sys.path.append(".")

from offline_analysis.utils.generator import FeaturesGenerator

debug = True


def main(debug=False):

    if debug == False:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", required=True, help="Config path")
        parser.add_argument("-s", "--server", required=True, help="Server path")
        parser.add_argument("-a", "--author", required=False, help="Author name")

        options = parser.parse_args()
        server = options.server
        author = options.author
        config = options.config

    else:
        config = "./test/config/test.yaml"
        server = "/Users/raph/OMIND_SERVER"
        author = "Raph"

    with open(config) as config_file:
        try:
            config = yaml.load(config_file)
        except yaml.YAMLError as exc:
            sys.exit(f"Could not parse: {config_file}: {exc}")

    generator = FeaturesGenerator(server_path=server, author = author)
    generator.set_loader(**config["inputs"])
    generator.set_logger(config["output"])
    generator.set_pipelines(config["pipelines"])
    _ = generator.run()
    generator.save(config["output"])
    logging.info("Done")


if __name__ == '__main__':
    main(debug)

    print(f"*** exiting '{__file__}' ***")
