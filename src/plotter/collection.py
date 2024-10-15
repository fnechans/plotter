from typing import Optional, List, Dict, Union
from ROOT import TH1
from .dataset import dataset, sumOfWeightHelper
import copy
import logging

log = logging.getLogger(__name__)


class normalizationHelper:
    """Small helper class to define normalization.

    Type of normalization is something which will be quite often shared
    and repatadly used, so this is better than to pass
    multiple arguments.
    """

    def __init__(
        self, normToOne=False, normByLumi=False, normByXS=False, normBySoW=False
    ) -> None:
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


def get_normalizationHelper(config):

    if config == "none":
        return normalizationHelper()
    if config == "events":
        return normalizationHelper(normByLumi=True, normByXS=True, normBySoW=True)
    if config == "one":
        return normalizationHelper(normToOne=True)
    else:
        raise RuntimeError("Unknown normalization config " + config)


class collection:
    """Manages collection of datasets
    and correct normalization of individual
    and combined histogram."""

    # TODO: need to rethink how sumOfWeightHelper is handled
    # both within collection and dataset
    def __init__(
        self,
        title: str,
        sow: Optional[sumOfWeightHelper] = None,
        scale_factor: Optional[float] = 1,
    ) -> None:
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
        self.scale_factor = scale_factor

    def __len__(self):
        return len(self.datasets)

    def add_dataset(self, ds: dataset) -> None:
        """Adds dataset to the collection."""
        self.datasets.append(ds)

    def add_collection(self, coll: "collection") -> None:
        """Adds all datasets from another collection."""
        self.datasets.extend(coll.datasets)

    def get_datasets(self) -> List[dataset]:
        return self.datasets

    def get_th(
        self,
        histoName: str,
        norm: Optional[normalizationHelper] = None,
        skipBad: bool = False,
    ) -> Optional[TH1]:
        """Gets histograms from all datasets
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
                log.warning(
                    f"Histogram {histoName} from collection {self.title} has integral 0."
                )
                log.warning("Cannot normalize to one!")
            else:
                collTH.Scale(1.0 / collTH.Integral())

        return collTH

    def norm_ds(self, th: TH1, ds: dataset, norm: normalizationHelper):
        """Normalizes histogram from a dataset"""

        if norm.byXS:
            th.Scale(ds.XS)
        if norm.bySoW:
            if self.sow is None:
                log.error(
                    "Trying to normalize by sum of weights,\n but none was provided!."
                )
                raise RuntimeError
            th.Scale(1.0 / ds.get_sumOfWeights(self.sow))
        if norm.byLumi:
            th.Scale(ds.lumi)


class SuperCollection:
    """Holds set of collections or SuperCollections, necessary for scaling collections"""

    def __init__(self, title: str, scale_factor: Optional[float] = 1):
        self.container: List[Union[collection, "SuperCollection"]] = []

        self.title = title
        self.scale_factor = scale_factor

    def __len__(self):
        return len(self.container)

    def add(self, col: Union[collection, "SuperCollection"]):

        self.container.append(col)

    def get_th(
        self,
        histoName: str,
        norm: Optional[normalizationHelper] = None,
        skipBad: bool = False,
    ) -> Optional[TH1]:
        """Gets histograms from all datasets
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

        if len(self.container) == 0:
            raise RuntimeError(f"Collection {self.title} is empty!\n Add datasets!")

        norm_orig = None
        if norm:
            norm_orig = copy.copy(norm)
            if norm.toOne:
                norm.toOne = (
                    False  # need to first add contributions, and normalize at the end.
                )

        collTH: Optional[TH1] = None
        for col in self.container:

            hist = col.get_th(histoName, norm, skipBad)

            if collTH:
                collTH.Add(hist)
            else:
                collTH = hist

        if collTH is None:
            return None

        # collection scalling
        collTH.Scale(self.scale_factor)

        if norm_orig is not None and norm_orig.toOne:
            if collTH.Integral() == 0:
                log.warning(
                    f"Histogram {histoName} from collection {self.title} has integral 0."
                )
                log.warning("Cannot normalize to one!")
            else:
                collTH.Scale(1.0 / collTH.Integral())

        return collTH


class CollectionContainer:
    """Manages a set of collections"""

    def __init__(self):
        self.container: Dict[Union[collection, SuperCollection]] = {}

    def __getitem__(self, index) -> Union[collection, SuperCollection]:
        return self.container[index]

    def add_dataset(self, ds: dataset, sow: Optional[sumOfWeightHelper] = None) -> None:
        """Add dataset and create a correponsing collection in the librarly"""

        col = collection(ds.name, sow)
        col.add_dataset(ds)

        self.add_collection(ds.name, col)

    def _exist_check(self, col_name):

        if col_name in self.container.keys():
            element = self.container[col_name]

            log.error(
                f"Element {col_name} already exists in container with title {element.title}" +
                f" It is {element.__class__.__name__} type of size " + str(len(element)) + ". Keeping old!"
            )
            if isinstance(element, collection):
                if len(element) == 1:
                    log.debug(
                        f"Old collection is a dataset: {element.datasets[0].path}"
                    )

            return True
        return False

    def add_collection(self, col_name, col: collection) -> None:
        """Add collection to the library"""

        if self._exist_check(col_name):
            if len(col) == 1:
                log.debug(f"New collection is a dataset : {col.datasets[0].path}")
            return

        self.container[col_name] = col

    def add_supercollection(self, col_name, col: SuperCollection) -> None:
        """Add supercollection to the library"""

        if self._exist_check(col_name):
            return

        self.container[col_name] = col

    def add_collections_by_name(
        self,
        col_name: str,
        col_title: str,
        components: List,
        sow: Optional[sumOfWeightHelper] = None,
        scale_factor: Optional[float] = 1,
    ) -> None:
        """Add collection by specifying their name. Internally the function will check if corresponding dataset exist"""

        if self._exist_check(col_name):
            raise RuntimeError

        supercollection = SuperCollection(col_title, scale_factor)
        for name in components:
            if name not in self.container.keys():
                log.warning(
                    f"Collection {name} does not exist, cannot be added to SuperCollection {col_name}"
                )
                continue

            element = self.container[name]
            # for collections which have scale_factor 1, one could include it in collection first.
            # We ignore this here and treat all as SuperCollections
            supercollection.add(element)

        if len(supercollection):
            self.add_supercollection(col_name, supercollection)
