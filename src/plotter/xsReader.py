from typing import List, Dict

import logging

log = logging.getLogger(__name__)


class _xs:
    def __init__(self) -> None:
        self.XS = 1.0
        self.kFactor = 1.0
        self.filtEff = 1.0

    def get_xs(self):
        return self.XS * self.kFactor * self.filtEff

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _xs):
            raise NotImplementedError("Only _xs can be compared!")
        return self.get_xs() - other.get_xs() == 0


class xsReader:
    def __init__(self) -> None:
        self.XSsection: Dict[str, _xs] = {}

    def add_files(self, filePaths: List[str]):
        for filePath in filePaths:
            self.add_file(filePath)

    @staticmethod
    def string2float(msg: str, string: str) -> float:
        new_str = string.strip()
        if new_str == "NULL":
            log.warning(f"{msg}String is `NULL`, returning 1!")
            return 1
        return float(new_str)

    def add_file(self, filePath: str) -> None:
        with open(filePath, "r") as xsFile:
            for line in xsFile.readlines():
                if line == "" or line[0] == "#" or "SampleID" in line:
                    continue
                split = line.split(",")
                if len(split) < 7:
                    continue
                dsid = split[0].strip()
                xs = _xs()
                xs.XS = xsReader.string2float(f"DSID {dsid} XS: ", split[1])
                xs.kFactor = xsReader.string2float(
                    f"DSID {dsid} k-factor: ", split[2]
                )
                xs.filtEff = xsReader.string2float(
                    f"DSID {dsid} filter efficiency: ", split[3]
                )
                if dsid in self.XSsection.keys():
                    if self.XSsection[dsid] == xs:
                        log.warning(f"DSID {dsid} already in XSsection, skipping!")
                        continue
                    else:
                        log.error(f"DSID {dsid} already in XSsection and has different XS!")
                        raise RuntimeError
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
