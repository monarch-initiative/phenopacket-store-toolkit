import argparse
import logging
import sys

import ppktstore
import ppktstore.release


def main(argv) -> int:
    """
    Phenopacket-store CLI
    """
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="ppktstore",
        formatter_class=argparse.RawTextHelpFormatter,
        description=main.__doc__,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=ppktstore.__version__),
    )

    # generate subparsers/subcommands
    subparsers = parser.add_subparsers(dest="command")

    # #################### ------------- `package` ------------- ####################
    parser_package = subparsers.add_parser(
        "package", help="Gather all phenopackets into a release archive"
    )
    parser_package.add_argument(
        "--notebook-dir", default="notebooks", help="path to cohorts directory"
    )
    parser_package.add_argument(
        "--format", nargs="*", type=str, default=("zip",), choices=("zip", "tgz")
    )
    parser_package.add_argument(
        "--release-tag",
        type=str,
        help="the release identifier, and also the name of the top-level folder where all cohorts will be placed",
    )
    parser_package.add_argument(
        "--output",
        required=False,
        default="all_phenopackets",
        help="where to write the release archive",
    )

    # #################### ------------- `qc` ------------------ ####################
    parser_check = subparsers.add_parser("qc", help="Q/C phenopackets")
    parser_check.add_argument(
        "--notebook-dir", default="notebooks", help="path to cohorts directory"
    )

    # #################### ------------- `report` -------------- ####################
    report = subparsers.add_parser("report", help="Generate reports")
    subparsers_report = report.add_subparsers(dest="report_command")

    parser_collections = subparsers_report.add_parser(
        "collections", help="Generate collections report"
    )
    parser_collections.add_argument(
        "--notebook-dir", default="notebooks", help="path to cohorts directory"
    )
    parser_collections.add_argument(
        "--notebook-dir-url",
        default="https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks",
        help="URL pointing to notebooks folder on GitHub",
    )
    parser_collections.add_argument(
        "--output", help="where to generate the collections report"
    )

    if len(argv) == 0:
        parser.print_help()
        return 1

    args = parser.parse_args(argv)

    logger = logging.getLogger(__name__)
    if args.command == "package":
        store = read_phenopacket_store(
            notebook_dir=args.notebook_dir,
            logger=logger,
        )
        from ppktstore.release.archive import package_phenopackets

        return package_phenopackets(
            store=store,
            formats=args.format,
            filename=args.output,
            top_level_folder=args.top_level_dir,
            logger=logger,
        )
    elif args.command == "qc":
        store = read_phenopacket_store(
            notebook_dir=args.notebook_dir,
            logger=logger,
        )
        from ppktstore.release.qc import qc_phenopackets

        return qc_phenopackets(
            store=store,
            logger=logger,
        )
    elif args.command == "report":
        if args.report_command == "collections":
            from ppktstore.release.report import generate_collections_report

            return generate_collections_report(
                notebook_dir=args.notebook_dir,
                notebook_dir_url=args.notebook_dir_url,
                output=args.output,
                logger=logger,
            )
        else:
            report.print_help()
            return 1
    else:
        parser.print_help()
        return 1


def read_phenopacket_store(
    notebook_dir: str,
    logger: logging.Logger,
) -> ppktstore.model.PhenopacketStore:
    logger.info("Reading phenopackets at `%s`", notebook_dir)
    phenopacket_store = ppktstore.model.PhenopacketStore.from_notebook_dir(notebook_dir)
    logger.info(
        "Read %d cohorts with %d phenopackets",
        phenopacket_store.cohort_count(),
        phenopacket_store.phenopacket_count(),
    )
    return phenopacket_store


def setup_logging():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(name)-20s %(levelname)-3s : %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
