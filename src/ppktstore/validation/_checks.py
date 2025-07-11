from ._api import PhenopacketStoreAuditor
from ..model import PhenopacketStore
from stairval.notepad import Notepad
from collections import Counter, defaultdict


class UniquePhenopacketId(PhenopacketStoreAuditor):
    """
    Check that phenopacket id is unique within the entire phenopacket store.
    """

    def id(self) -> str:
        return "unique_ps_id_check"

    def audit(
        self,
        item: PhenopacketStore,
        notepad: Notepad
    ):
        id_counter = Counter()
        pp_id2cohort = defaultdict(set)
        if len(item.cohorts()) > 1:
            for cohort in item.cohorts():
                for pp_info in cohort.phenopackets:
                    pp_id = pp_info.phenopacket.id
                    pp_id2cohort[pp_id].add(cohort.name)
                    id_counter[pp_id] += 1

            repeated = {pp_id: count for pp_id, count in id_counter.items() if count > 1}

            for pp_id, count in repeated.items():
                msg = f"`{pp_id}` is present in {count} cohorts: {pp_id2cohort[pp_id]}"
                notepad.add_error(msg)