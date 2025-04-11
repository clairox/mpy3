import sys


def log(*values: object) -> None:
    sys.stdout.write("\r\033[K")
    sys.stdout.write(" ".join(str(v) for v in values))
    sys.stdout.flush()
