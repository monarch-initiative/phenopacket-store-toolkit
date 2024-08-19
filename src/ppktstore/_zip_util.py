import sys
import zipfile


def relative_to(
    a: zipfile.Path,
    b: zipfile.Path,
) -> str:
    if sys.version_info >= (3, 12):
        # The functionality seems to have been introduced in 3.12.
        return a.relative_to(b)
    else:
        a_str = str(a)
        b_str = str(b)
        return b_str.replace(a_str, '')
