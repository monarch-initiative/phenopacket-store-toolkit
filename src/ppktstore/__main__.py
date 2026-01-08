import argparse
import logging
import pathlib
import os
import sys

import hpotk

import ppktstore


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
        "package",
        help="Gather all phenopackets into a release archive",
    )
    parser_package.add_argument(
        "--notebook-dir",
        default="notebooks",
        help="path to cohorts directory",
    )
    parser_package.add_argument(
        "--format",
        nargs="*",
        type=str,
        default=("zip",),
        choices=("zip", "tgz"),
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
        "--notebook-dir",
        default="notebooks",
        help="path to cohorts directory",
    )
    parser_check.add_argument(
        "--hpo",
        type=pathlib.Path,
        default=None,
        help="path to hp.json file",
    )
    parser_check.add_argument(
        "--hpo-release",
        type=str,
        default=None,
        help="HPO version to use (e.g. `v2024-04-26`)",
    )

    # #################### ------------- `report` -------------- ####################
    report = subparsers.add_parser("report", help="Generate reports")
    subparsers_report = report.add_subparsers(dest="subcommand")

    parser_collections = subparsers_report.add_parser(
        "collections",
        help="Generate collections report",
    )
    parser_collections.add_argument(
        "--notebook-dir",
        default="notebooks",
        help="path to cohorts directory",
    )
    parser_collections.add_argument(
        "--notebook-dir-url",
        default="https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks",
        help="URL pointing to notebooks folder on GitHub",
    )
    parser_collections.add_argument(
        "--output",
        help="where to generate the collections report",
    )

    # #################### ------------- `export` -------------- ####################

    parser_export = subparsers.add_parser(
        "export",
        help="Export a phenopackets, cohorts, or families",
    )
    subparsers_export = parser_export.add_subparsers(dest="subcommand")

    # #################### ------------- `export | phenopackets` ####################
    parser_export_phenopackets = subparsers_export.add_parser(
        "phenopackets",
        help="export phenopackets from phenopacket store",
    )
    parser_export_phenopackets.add_argument(
        "-r",
        "--release",
        default=None,
        help="phenopacket store release tag (default: latest)",
    )
    parser_export_phenopackets.add_argument(
        "-f",
        "--format",
        type=str,
        default="json",
        choices=("json", "pb"),
        help="phenopacket file format (default: json)",
    )
    parser_export_phenopackets.add_argument(
        "-o",
        "--outdir",
        type=pathlib.Path,
        default=pathlib.Path(os.getcwd()),
        help="path to directory where to export",
    )
    parser_export_phenopackets.add_argument(
        "cohort",
        type=str,
        help="name of the cohort to export",
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
            release_tag=args.release_tag,
            logger=logger,
        )
    elif args.command == "qc":
        if args.hpo is None and args.hpo_release is None:
            print("Either `--hpo` or `--hpo-release` must be set!")
            return 1
        if args.hpo is not None:
            hpo = hpotk.load_minimal_ontology(str(args.hpo))
        else:
            store = hpotk.configure_ontology_store()
            hpo = store.load_minimal_hpo(release=args.hpo_release)

        logger.info(f"Using HPO version {hpo.version}")

        store = read_phenopacket_store(
            notebook_dir=args.notebook_dir,
            logger=logger,
        )
        from ppktstore.validation import qc_phenopacket_store

        return qc_phenopacket_store(
            store=store,
            hpo=hpo,
            logger=logger,
        )
    elif args.command == "report":
        if args.subcommand == "collections":
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
    elif args.command == "export":
        if args.subcommand == "phenopackets":
            from ppktstore.registry import configure_phenopacket_registry

            if args.format not in ("json", "pb"):
                logger.error(
                    "format must be one of ('json', 'pb') but was %s",
                    args.format,
                )
                return 1

            release = getattr(args, "release") if hasattr(args, "release") else None
            registry = configure_phenopacket_registry()

            with registry.open_phenopacket_store(release=release) as ps:
                try:
                    ps.cohort_for_name(args.cohort).export_phenopackets_to_directory(
                        path=args.outdir,
                        format=args.format,
                    )
                except KeyError:
                    logger.error(
                        "Cohort %s was not found in phenopacket store",
                        args.cohort,
                    )
            return 0
        else:
            parser.print_help()
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
        "%(asctime)s %(name)-20s %(levelname)-3s : %(message)s",
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
