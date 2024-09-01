import typing

from collections import Counter, defaultdict

from stairval.notepad import Notepad

from ppktstore.model import PhenopacketStore

from ._api import PhenopacketStoreAuditor


class UniqueIdsCheck(PhenopacketStoreAuditor):
    """
    Check that phenopacket id is unique within the entire phenopacket store.
    """

    def make_id(self) -> str:
        return "unique_ids_check"

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):
        id_counter = Counter()
        pp_id2cohort = defaultdict(set)

        for cohort in item.cohorts():
            for pp_info in cohort.phenopackets:
                pp_id = pp_info.phenopacket.id
                pp_id2cohort[pp_id].add(cohort.name)
                id_counter[pp_id] += 1

        repeated = {pp_id: count for pp_id, count in id_counter.items() if count > 1}

        for pp_id, count in repeated.items():
            msg = f"`{pp_id}` is present in {count} cohorts: {pp_id2cohort[pp_id]}"
            notepad.add_error(msg)


class NoUnwantedCharactersCheck(PhenopacketStoreAuditor):
    """
    Check that phenopacket elements do not include any unwanted characters (e.g. whitespace).
    """

    @staticmethod
    def no_whitespace(
        whitespaces: typing.Iterable['str'] = ("\t", "\n", "\r\n"),
    ) -> "NoUnwantedCharactersCheck":
        return NoUnwantedCharactersCheck(whitespaces)

    def __init__(
        self,
        unwanted: typing.Iterable[str],
    ):
        self._unwanted = set(unwanted)

    def make_id(self) -> str:
        return "unwanted_characters_check"

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):
        for cohort in item.cohorts():
            cohort_pad = notepad.add_subsection(cohort.name)
            for pp_info in cohort.phenopackets:
                pp_pad = cohort_pad.add_subsection(pp_info.path)
                pp = pp_info.phenopacket
                self._check_unwanted_characters(pp.id, pp_pad.add_subsection("id"))
                _, subject_id_pad = pp_pad.add_subsections("subject", "id")
                self._check_unwanted_characters(pp.subject.id, subject_id_pad)

                # Disease name in diseases and variant interpretations
                disease_pad = pp_pad.add_subsection("disease")
                for i, disease in enumerate(pp.diseases):
                    _, _, label_pad = disease_pad.add_subsections(f"#{i}", "term", "label")
                    self._check_unwanted_characters(disease.term.label, label_pad)

                interpretation_pad = pp_pad.add_subsection("interpretations")
                for i, interpretation in enumerate(pp.interpretations):
                    id_pad = interpretation_pad.add_subsection("id")
                    self._check_unwanted_characters(interpretation.id, id_pad)
                    _, _, label_pad = interpretation_pad.add_subsections("diagnosis", "disease", "label")
                    self._check_unwanted_characters(
                        interpretation.diagnosis.disease.label, label_pad
                    )

                # PubMed title
                _, ers_pad = pp_pad.add_subsections("meta_data", "external_references")
                for i, er in enumerate(pp.meta_data.external_references):
                    _, er_pad = ers_pad.add_subsections(f"#{i}", "description")
                    self._check_unwanted_characters(er.description, er_pad)

    def _check_unwanted_characters(
        self,
        value: str,
        notepad: Notepad,
    ):
        for ch in value:
            if ch in self._unwanted:
                notepad.add_error(f"`{value}` includes a forbidden character `{ch}`")


class DefaultPhenopacketStoreAuditor(PhenopacketStoreAuditor):

    def __init__(
        self,
        checks: typing.Iterable[PhenopacketStoreAuditor],
    ):
        self._checks = tuple(checks)
        self._id = '[' + ', '.join(check.make_id() for check in self._checks) + ']'

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad,
    ):
        for check in self._checks:
            sub_notepad = notepad.add_subsection(check.make_id())
            check.audit(
                item=item,
                notepad=sub_notepad,
            )

    def make_id(self) -> str:
        return self._id
