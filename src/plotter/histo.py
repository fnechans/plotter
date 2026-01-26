import ROOT
from ROOT import TH1
from . import thHelper
from . import loader
from typing import Optional, Dict, Any, List, Union, Tuple
from plotter.plottingbase import Plottable

import logging

log = logging.getLogger(__name__)

ROOT.TH1.AddDirectory(False)


class histo(Plottable):
    """Wrapper class around TH1, setups the main properties
    + contains few usefull function (e.g. divide_ratio)

    The idea is that the rather short constructor holds
    all properties needed for plotting, all the others
    are handled by other classes
    """

    def __init__(
        self,
        title: str,
        th: TH1,
        linecolor: int = ROOT.kBlack,
        fillcolor: Optional[int] = 0,
        drawoption: str = "",
        configPath: str = "",
    ) -> None:
        """
        Arguments:
            th (``TH1``): ROOT histogram
            linecolor (``int``): color of the histogram line
            fillcolor (``int/None``): color of the histogram fill,
                can be None
        """
        self.th = th
        self.title = title
        super().__init__()

        self.linecolor = linecolor
        self.fillcolor = fillcolor
        self.config = loader.load_config(configPath) if configPath != "" else {}
        self.apply_all_style()
        self.drawoption = drawoption

        self.isTH1 = th.InheritsFrom("TH1")
        self.isTGraph = th.InheritsFrom("TGraph")

    def apply_all_style(self):
        self.th.SetTitle(self.title)

        if self.config != "":
            self.style_histo(self.config)

    def draw(self, suffix: str = "", drawoption: Optional[str] = None) -> None:
        """TH1.Draw wrapper,

        Arguments
            option (``str``): if want to overwrite self.option
            suffix (``str``): suffix afteert option, mainly for "same"
        """
        if drawoption is None:
            drawoption = self.drawoption

        self.th.Draw(drawoption + suffix)

    def divide(self, otherHisto: "histo", option: str = "") -> bool:
        """Add ROOT::TH1::Divide to histo level

        Arguments:
            otherHist (``histo``): histogram to divide by
            option (``str``): if B then binomial errors"""
        return self.th.Divide(self.th, otherHisto.th, 1, 1, option)

    def divide_ratio(self, otherHisto: "histo"):
        """For ratio, we do not to take into account
        errors of otherHisto!

        Uses function from thHelper

        Arguments:
            otherHisto (``histo``): histo to be divided by
        """
        thHelper.divide_ratio(self.th, otherHisto.th)

    def get_ratio(
        self, otherHisto: "histo", suffix: str = "ratio", fillToLine: bool = False
    ) -> "histo":
        """Returns clone of the saved histogram and divides by otherHist.
        All the other properties are copied.

        Arguments:
            otherHist (``histo``): histogram to divide by
            suffix (``str``): suffix behind the name of the histogram
            fillToLine (``bool``): switch from fill to line
        """

        hratio = self.clone(th_suffix=suffix)
        # TODO: histo of different type?
        if self.isTH1:
            thHelper.divide_ratio(hratio.th, otherHisto.th)
        elif self.isTGraph:
            thHelper.divide_ratio_graph(hratio.th, otherHisto.th)
        else:
            log.error("Cannot divide histo, not TH1 or TGraph")
            raise TypeError("Cannot divide histo, not TH1 or TGraph")
        # switch colors if requested
        fillcolor = None if fillToLine else self.fillcolor
        if fillcolor is None:
            fillcolor = ROOT.kWhite

        # to satisfy mypy first assign linecolor
        linecolor = self.linecolor
        if fillToLine and self.fillcolor is not None:
            linecolor = self.fillcolor

        hratio.fillcolor = fillcolor
        hratio.linecolor = linecolor
        return hratio

    def style_histo(self, style: Dict[str, Any]) -> None:
        """Applies style to the histo

        Arguments:
            style (``Dict[str, Any]``): style config
        """

        log.debug("Updating histo style")

        for opt, set in style.items():
            if "markersize" in opt:
                self.th.SetMarkerSize(set)
            elif "fillstyle" in opt:
                self.th.SetFillStyle(set)
            elif "linestyle" in opt:
                self.th.SetLineStyle(set)
            elif "drawoption" in opt:
                self.drawoption = set
            else:
                log.error(f"Unknown option {opt}")
                raise RuntimeError

    def _edges_from_tuple(
        self, edges: List[float], binning: List[Tuple[int, float]]
    ) -> List[float]:
        for bindef in binning:
            (nbins, width) = bindef
            for i in range(nbins):
                w = edges[-1] + width
                if w <= self.th.GetXaxis().GetXmax():
                    edges.append(w)
                else:
                    log.warning(
                        "Rebinning requires either int or list, got binning that exceeds histogram range"
                    )
        last_edge = edges[-1]
        if last_edge < self.th.GetXaxis().GetXmax():
            edges.append(self.th.GetXaxis().GetXmax())
        return edges

    def rebin(
        self,
        binning: Union[int, List[float], Tuple[float, list[Tuple[int, float]]]] = [],
    ):
        """Rebins histogram either based on nbin or binning.

        - If variable is int it merges given number of bins (so TH1::Rebin)
        - If it is a list
           - if it is list of numbers creates new histogram with that binning.
           - if the format is [xmin, (nbins, width), ...] it creates
             new histogram with given binning, where each tuple defines
        Arguments:
            binning (``Union[int, List[Union[float, tuple]]]``): binning used in the new histogram
        """

        if isinstance(binning, int):
            self.th.Rebin(binning)
            return

        # binning [xmin, x1, x2, ... ]
        if isinstance(binning, list) and all(isinstance(x, float) for x in binning):

            if len(binning) < 2:
                log.error("Rebinning requires either int or list, got empty list")
                raise ValueError(
                    "Rebinning requires either int or list, got empty list"
                )

            binedges = binning

        # binning [ xmin, {nbinx, width}, {nbinx,width}, ...]
        elif (
            isinstance(binning, tuple)
            and isinstance(binning[0], float)
            and isinstance(binning[1], list)
            and all(isinstance(x, tuple) for x in binning[1])
        ):
            binedges = self._edges_from_tuple([binning[0]], binning[1])
        else:
            raise ValueError(
                f"Binning {binning} does not have correct format, has to be either:\n"
                " - int\n"
                " - list of numbers\n"
                " - tuple of float + list of tuples (number of bins, bin width)"
            )

        self.th = thHelper.rebin(self.th, binedges, False)
        self.apply_all_style()

    def clone(self, th_suffix: Optional[str] = None, histo_title: Optional[str] = None):

        if histo_title is None:
            histo_title = self.title

        hname = histo_title
        if th_suffix is not None:
            hname = histo_title + "_" + th_suffix

        h = histo(histo_title, self.th.Clone(hname))
        h.decorate(self)

        return h

    def add(self, otherHisto: Union["histo", List["histo"]]):
        if isinstance(otherHisto, histo):
            self.th.Add(otherHisto.th)
        elif isinstance(otherHisto, list):
            for h in otherHisto:
                if not isinstance(h, histo):
                    raise TypeError("All elements must be of type histo")
                self.th.Add(h.th)
        else:
            raise TypeError("Argument must be a histo or list of histo")

    def scale(self, factor: float):
        self.th.Scale(factor)

    def normalize(self):
        integral = self.th.Integral()
        if integral != 0:
            self.th.Scale(1.0 / integral)
