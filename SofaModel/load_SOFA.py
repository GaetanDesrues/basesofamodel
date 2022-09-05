import logging


def load_SOFA():
    import os
    import sys

    sofa_build = os.environ.get("SOFA_ROOT")
    if not sofa_build:
        log.error(
            "The env variable `SOFA_ROOT` is required\n"
            "from: 'Model3D/basesofamodel/load_SOFA.py'"
        )
        raise SystemExit
    if not os.path.isdir(sofa_build):
        log.error(f"{sofa_build!r} does not exist")
        raise SystemExit

    sys.path.extend(
        (
            f"{sofa_build}/lib/python3/site-packages",
            f"{sofa_build}/lib/python/site-packages",
        )
    )
    os.environ["SOFA_ROOT"] = sofa_build
    os.environ["SOFAPYTHON3_ROOT"] = sofa_build

    log.info(f"--> Found SOFA: {sofa_build!r}")


log = logging.getLogger(__name__)
