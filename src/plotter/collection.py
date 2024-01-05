from typing import Optional, List
from ROOT import TH1
from .dataset import dataset, sumOfWeightHelper

import logging
log = logging.getLogger(__name__)


class normalizationHelper:
    """ Small helper class to define normalization.

    Type of normalization is something which will be quite often shared
    and repatadly used, so this is better than to pass
    multiple arguments.
    """

    def __init__(self, normToOne=False, normByLumi=False,
                 normByXS=False, normBySoW=False) -> None:
        """
        Arguments:
            normToOne (``bool``): if True: after all steps,
                normalize by Integral
            normbyLumi (``bool``): if True:luminosity of given collection
                is applied
            normbyXSX (``bool``): if True: cross-section of given dataset
                is applied
            normbySoW (``bool``): if True: each dataset is normalized
                by sum of weights
        """

        self.toOne = normToOne
        self.byLumi = normByLumi
        self.byXS = normByXS
        self.bySoW = normBySoW


class collection:
    """ Manages collection of datasets
    and correct normalization of individual
    and combined histogram. """

    # TODO: need to rethink how sumOfWeightHelper is handled
    # both within collection and dataset
    def __init__(self, title: str,
                 sow: Optional[sumOfWeightHelper] = None) -> None:
        """
        Arguments:
            title (``str``): title of the sample,
                used e.g. in plotting
            sow (``sumOfWeightHelper```): defines where the sumOfWeight factor
                can be found, see the sumOfWeightHelper class in dataset.py
        """
        self.title = title
        self.sow = sow

        # list of samples in the collection
        self.datasets: List[dataset] = []

    def add_dataset(self, ds: dataset) -> None:
        """ Adds dataset to the collection."""
        self.datasets.append(ds)

    def add_collection(self, coll: "collection") -> None:
        """ Adds all datasets from another collection."""
        self.datasets.extend(coll.datasets)

    def get_th(self, histoName: str, norm: Optional[normalizationHelper] = None, skipBad: bool = False) -> Optional[TH1]:
        """ Gets histograms from all datasets
        and correctly combines and normalizes them

        Arguments:
            histoName (``str``): name/path of histogram in given file
            norm (``normalizationHelper``): defines normalization of the
                collection, see normalizationHelper class for details
            skipBad (``bool``): if histogram or file does not exist,
                or is corrupted, it is skipped instead of raising error

        Returns:
            Combined histogram (``TH1``)
        """

        if len(self.datasets) == 0:
            raise RuntimeError(f"Collection {self.title} is empty!\n Add datasets!")

        collTH: Optional[TH1] = None
        for ds in self.datasets:
            dsTH = ds.get(histoName, skipBad)
            if dsTH is None:
                if not skipBad:
                    log.error("Got bad histogram from the dataset.")
                    raise RuntimeError
                continue

            if norm is not None:
                self.norm_ds(dsTH, ds, norm)

            if collTH:
                collTH.Add(dsTH)
            else:
                collTH = dsTH

        if collTH is None:
            return None

        if norm is not None and norm.toOne:
            if collTH.Integral() == 0:
                log.warning(f"Histogram {histoName} from collection {self.title} has integral 0.")
                log.warning("Cannot normalize to one!")
            else:
                collTH.Scale(1./collTH.Integral())

        return collTH

    def norm_ds(self, th: TH1, ds: dataset, norm: normalizationHelper):
        """ Normalizes histogram from a dataset
        """
        if norm.byXS:
            th.Scale(ds.XS)
        if norm.bySoW:
            if self.sow is None:
                log.error("Trying to normalize by sum of weights,\n but none was provided!.")
                raise RuntimeError
            th.Scale(1./ds.get_sumOfWeights(self.sow))
        if norm.byLumi:
            th.Scale(ds.lumi)
