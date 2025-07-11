import click
import logging
import pathlib
import os
import sys

import ppktstore


# --- Click CLI Implementation ---


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(ppktstore.__version__, prog_name="ppktstore")
def cli():
    """Phenopacket-store CLI"""
    setup_logging()


@cli.command()
@click.option("--notebook-dir", help="path to cohorts directory", required=True)
@click.option("--format", multiple=True, type=click.Choice(["zip", "tgz"]), default=["zip"], help="archive format(s)")
@click.option("--release-tag", type=str, help="release identifier and top-level folder name")
@click.option("--output", default="all_phenopackets", help="where to write the release archive")
def package(notebook_dir, format, release_tag, output):
    """Gather all phenopackets into a release archive"""
    logger = logging.getLogger(__name__)
    store = read_phenopacket_store(notebook_dir=notebook_dir, logger=logger)
    from ppktstore.release.archive import package_phenopackets
    return package_phenopackets(
        store=store,
        formats=format,
        filename=output,
        release_tag=release_tag,
        logger=logger,
    )


@cli.command()
@click.option("--notebook-dir", help="path to cohorts directory", required=True)
def qc(notebook_dir):
    """Q/C phenopackets"""
    logger = logging.getLogger(__name__)
    store = read_phenopacket_store(notebook_dir=notebook_dir, logger=logger)
    from ppktstore.validation import qc_phenopacket_store
    return qc_phenopacket_store(store=store, logger=logger)


@cli.group()
def report():
    """Generate reports"""
    pass


@report.command("collections")
@click.option("--notebook-dir", help="path to cohorts directory", required=True)
@click.option(
    "--notebook-dir-url",
    default="https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks",
    help="URL pointing to notebooks folder on GitHub",
)
@click.option("--output", help="where to generate the collections report")
def collections(notebook_dir, notebook_dir_url, output):
    """Generate collections report"""
    logger = logging.getLogger(__name__)
    from ppktstore.release.report import generate_collections_report
    return generate_collections_report(
        notebook_dir=notebook_dir,
        notebook_dir_url=notebook_dir_url,
        output=output,
        logger=logger,
    )


@cli.group()
def export():
    """Export a phenopackets, cohorts, or families"""
    pass


@export.command("phenopackets")
@click.option("-r", "--release", default=None, help="phenopacket store release tag (default: latest)")
@click.option("-f", "--format", type=click.Choice(["json", "pb"]), default="json", show_default=True, help="phenopacket file format")
@click.option("-o", "--outdir", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=pathlib.Path), default=pathlib.Path(os.getcwd()), help="path to directory where to export")
@click.argument("cohort")
def export_phenopackets(release, format, outdir, cohort):
    """Export phenopackets from phenopacket store"""
    logger = logging.getLogger(__name__)
    from ppktstore.registry import configure_phenopacket_registry
    if format not in ("json", "pb"):
        logger.error("format must be one of ('json', 'pb') but was %s", format)
        sys.exit(1)
    registry = configure_phenopacket_registry()
    with registry.open_phenopacket_store(release=release) as ps:
        try:
            ps.cohort_for_name(cohort).export_phenopackets_to_directory(
                path=outdir,
                format=format,
            )
        except KeyError:
            logger.error("Cohort %s was not found in phenopacket store", cohort)
    sys.exit(0)


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
    cli()
