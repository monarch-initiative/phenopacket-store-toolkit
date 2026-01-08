import sys


def relative_to(
    a,
    b,
) -> str:
    if sys.version_info >= (3, 12):
        # The functionality seems to have been introduced in 3.12.
        return str(a.relative_to(b))
    else:
        a_str = str(a)
        b_str = str(b)
        return a_str.replace(b_str, "")
