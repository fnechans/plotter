import ROOT
from ROOT import TH1
from . import thHelper
from . import loader
from typing import Optional, Dict, Any

import logging
log = logging.getLogger(__name__)

ROOT.TH1.AddDirectory(False)


class histo:
    """ Wrapper class around TH1, setups the main properties
        + contains few usefull function (e.g. divide_ratio)

        The idea is that the rather short constructor holds
        all properties needed for plotting, all the others
        are handled by other classes
    """

    def __init__(self, title: str, th: TH1, lineColor: int = ROOT.kBlack,
                 fillColor: Optional[int] = None, drawOption: str = "",
                 configPath: str = "") -> None:
        """
        Arguments:
            th (``TH1``): ROOT histogram
            lineColor (``int``): color of the histogram line
            fillColor (``int/None``): color of the histogram fill,
                can be None
        """
        self.th = th
        self.title = title
        self.lineColor = lineColor
        self.fillColor = fillColor

        th.SetTitle(title)
        self.set_lineColor(lineColor)
        if fillColor is not None:
            self.set_fillColor(fillColor)

        self.config: Dict[str, Any] = {}
        self.drawOption = ""
        if configPath != "":
            self.config = loader.load_config(configPath)
            self.style_histo(self.config)
        if drawOption!= "":
            self.drawOption = drawOption

    def set_fillColor(self, fillColor: int):
        """ Sets fill color """
        self.fillColor = fillColor
        self.th.SetFillColor(fillColor)

    def set_lineColor(self, lineColor: int):
        """ Sets line color """
        self.lineColor = lineColor
        self.th.SetLineColor(lineColor)

    def draw(self, suffix: str = "", drawOption: Optional[str] = None) -> None:
        """ TH1.Draw wrapper,

        Arguments
            option (``str``): if want to overwrite self.option
            suffix (``str``): suffix afteert option, mainly for "same"
        """
        if drawOption is None:
            drawOption = self.drawOption
        self.th.Draw(drawOption+suffix)

    def divide(self, otherHisto: "histo", option: str = "") -> bool:
        """ Add ROOT::TH1::Divide to histo level

        Arguments:
            otherHist (``histo``): histogram to divide by
            option (``str``): if B then binomial errors """
        return self.th.Divide(self.th, otherHisto.th, 1, 1, option)

    def divide_ratio(self, otherHisto: "histo"):
        """ For ratio, we do not to take into account
        errors of otherHisto!

        Uses function from thHelper

        Arguments:
            otherHisto (``histo``): histo to be divided by
        """
        thHelper.divide_ratio(self.th, otherHisto.th)

    def get_ratio(self, otherHisto: "histo", suffix: str = "ratio",
                  fillToLine: bool = False) -> "histo":
        """ Returns clone of the saved histogram and divides by otherHist.
        All the other properties are copied.

        Arguments:
            otherHist (``histo``): histogram to divide by
            suffix (``str``): suffix behind the name of the histogram
            fillToLine (``bool``): switch from fill to line
        """
        th = self.th.Clone(suffix)
        thHelper.divide_ratio(th, otherHisto.th)

        # switch colors if requested
        fillColor = None if fillToLine else self.fillColor
        if fillColor is None:
            th.SetFillColor(ROOT.kWhite)
        # to satisfy mypy first assign lineColor
        lineColor = self.lineColor
        if fillToLine and self.fillColor is not None:
            lineColor = self.fillColor

        return histo(self.title+"_"+suffix, th, lineColor=lineColor,
                     fillColor=fillColor, drawOption=self.drawOption)

    def style_histo(self, style: Dict[str, Any]) -> None:
        """ Applies style to the histo

        Arguments:
            style (``Dict[str, Any]``): style config
        """

        log.debug("Updating histo style")

        for opt, set in style.items():
            if "markerSize" in opt:
                self.th.SetMarkerSize(set)
            elif "fillStyle" in opt:
                self.th.SetFillStyle(set)
            elif "lineStyle" in opt:
                self.th.SetLineStyle(set)
            elif "drawOption" in opt:
                self.drawOption = set
            else:
                log.error(f"Unknown option {opt}")
                raise RuntimeError
