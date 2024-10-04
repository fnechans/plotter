import ROOT
from ROOT import TH1
from . import thHelper
from . import loader
from typing import Optional, Dict, Any, List, Union
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
        if drawoption != "":
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

    def rebin(self, binning: Union[int, List[float]] = []):
        """Rebins histogram either based on nbin or binning.

        If variable is int then just merges given number of bins (so TH1::Rebin),
        otherwise assume binning is list and creates new histogram with that binning.

        Arguments:
            binning (``Union[int, List[float]]``): binning used in the new histogram
        """

        if isinstance(binning, int):
            self.th.Rebin(binning)
            return

        self.th = thHelper.rebin(self.th, binning, False)
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
