def load_SOFA():
    import os
    import sys

    sofa_build = os.environ.get("SOFA_ROOT")
    if not sofa_build:
        sofa_build = "/home/gdesrues/Documents/sofa/v21.12/build_clion"
    if not os.path.isdir(sofa_build):
        print(f"{sofa_build!r} does not exist")
        sys.exit()

    sys.path.insert(0, f"{sofa_build}/lib/python3/site-packages")
    os.environ["SOFA_ROOT"] = sofa_build
    os.environ["SOFAPYTHON3_ROOT"] = sofa_build

    print(f"--> Found SOFA: {sofa_build!r}")
