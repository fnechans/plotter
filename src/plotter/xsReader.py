from typing import List, Dict

import logging
log = logging.getLogger(__name__)


class _xs:
    def __init__(self) -> None:
        self.XS = 1.
        self.kFactor = 1.
        self.filtEff = 1.

    def get_xs(self):
        return self.XS*self.kFactor*self.filtEff


class xsReader:
    def __init__(self) -> None:
        self.XSsection: Dict[str, _xs] = {}

    def add_files(self, filePaths: List[str]):
        for filePath in filePaths:
            self.add_file(filePath)

    def add_file(self, filePath: str) -> None:
        with open(filePath, "r") as xsFile:
            for line in xsFile.readlines():
                if line == "" or line[0] == "#" or "SampleID" in line:
                    continue
                split = line.split(",")
                if len(split) < 9:
                    continue
                dsid = split[0].strip()
                xs = _xs()
                xs.XS = float(split[1].strip())
                xs.kFactor = float(split[2].strip())
                xs.filtEff = float(split[3].strip())
                self.XSsection[dsid] = xs

    def get_xs(self, dsid: str, oneIfMissing: bool = False) -> float:
        if dsid not in self.XSsection.keys():
            if oneIfMissing:
                log.warning(f"DSID {dsid} not in any of added files!")
                log.warning("Returning 1")
                return 1
            log.error(f"DSID {dsid} not in any of added files!")
            raise RuntimeError
        return self.XSsection[dsid].get_xs()
