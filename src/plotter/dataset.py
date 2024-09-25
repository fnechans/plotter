from ROOT import TH1, TTree
from typing import Optional, Union
import os

# This way we can easily switch back to
# TFile from ROOT if needed
# Right now TFile2 does not provide
# any advantage for dataset but
# its derived class anyway
from .tfile2 import TFile2 as TFile

import logging

log = logging.getLogger(__name__)


class sumOfWeightHelper:
    """Small helper class to get sum of weight

    Since it is shared for whole analysis
    it is better to just pass one object.
    However, it is not global enough to have it shared
    globally or something.
    """

    def __init__(self, histoName: str, histoBin: int) -> None:
        """
        Arguments:
            histoName (``str``): name of histogram containing sum of weights
            histoBin (``int``): bin in historgam containing sum of weights
        """
        self.histoName = histoName
        self.histoBin = histoBin


class dataset:
    """Manages single ROOT TFile"""

    def __init__(self, title: str, path: str, XS: float = 1, lumi: float = 1) -> None:
        """
        Arguments:
            title (``str``): title of the sample,
                used e.g. in plotting
            path (``str``): path to the ROOT file
            XS (``float``): cross-section of the sample,
                (use 1 for data) /sumOfWeights and luminosity
                are treated independently
            lumi (``float``): luminosity of the sample
        """
        self.name = title
        # create absolute path in case context changes
        self.path = os.path.abspath(path)
        self.XS = XS
        self.lumi = lumi

        # dataset can be created even if it not used
        # (e.g. some central list of samples)
        # so do not open TFile until it is used
        self.tFile: TFile
        self.open = False

        # In some rare cases we want to simply
        # skip bad files and not throw error.
        # This is handled by following flag:
        self.goodFile = False

        # Sum of weights for normalization of MC,
        # when 0 not initiliazed
        self.sumOfWeights = 0

    def open_tfile(self, skipBad: bool = False) -> bool:
        """Opens TFile corresponding to the path,
        returns True if succesfull

        Arguments:
            skipBad (``bool``): if True, does not
                raise error on bad file, False by default

        Returns:
            True (``bool``) if succesful
        """

        # check if the file was already opened
        if not self.open:
            self.open = True
            self.tFile = TFile(self.path)
            # check if the file is not broken
            if self.tFile.IsZombie():
                log.error(f"Problem opening file {self.path}")
                if not skipBad:
                    raise RuntimeError
                return False
            else:
                log.debug(f"Success opening file {self.path}")
                self.goodFile = True
                return True
        else:
            return self.goodFile

    def get(
        self, objectName: str, skipBad: bool = False
    ) -> Optional[Union[TH1, TTree]]:
        """Returns Object (usually TH1) corresponding to the path

        Arguments:
            skipBad (``bool``): if True, does not
                raise error on bad file, False by default
        """

        # check status of the file and raise error
        # or return None in case of issues
        if not self.open:
            if not self.open_tfile(skipBad):
                if not skipBad:
                    log.error(f"Problem opening file {self.path}")
                    raise RuntimeError
                return None
        if self.goodFile:
            h = self.tFile.Get(objectName)
            if not h:  # is not None does not work for some reason
                log.error(f"Object {objectName} does not exist in dataset {self.name}!")
                raise RuntimeError
            return h
        return None

    def get_sumOfWeights(self, sow: sumOfWeightHelper) -> float:
        """Defines sum of weight of given dataset and returns it.
        The weight is saved so next time function is called the same
        value is simply returned.

        Arguments:
            sow (``sumOfWeightsHelper``): defines name of histogram
                and bin containing sumOfWeights
        """

        # TODO: This implementation assumes that sow,
        # and therefore sumOfWeights,
        # cannot change. Is this actually correct?

        # if it was already derived simply return
        if self.sumOfWeights != 0:
            return self.sumOfWeights

        # get histogram with sum of weights
        h = self.get(sow.histoName, False)

        if h is None:
            log.error(f"Histogram {sow.histoName} does not exist!")
            raise RuntimeError
        else:
            self.sumOfWeights = h.GetBinContent(sow.histoBin)
        # TODO Here I can imagine negative sum of weights
        # e.g. for some interferance sample but I have no idea
        # how to handle such cases
        assert self.sumOfWeights > 0, "Sum of weights should be positive!"

        return self.sumOfWeights
