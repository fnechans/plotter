from ROOT import TLegend
from typing import List
from .histo import histo

import logging
log = logging.getLogger(__name__)


class legend:
    """ Wrapper around TLegend"""
    def __init__(self, xMin: float = 0.58, xMax: float = 0.96,
                 height: float = 0.03, yMax: float = 0.94, nColumns: int = 1) -> None:
        """
        Arguments:
            xMin (``float``): lower x position of the legend
            xMax (``float``): upper x position of the legend
            yMin (``float``): lower y position of the legend
            yMax (``float``): upper y position of the legend
        """

        self.xMin = xMin
        self.xMax = xMax
        self.yMax = yMax
        self.height = height
        self.nCol = nColumns

        self.histos: List[histo] = []

    def add_histo(self, h: histo):
        """ Add histo to the legend """

        # TODO IMPROVE BY USING DECORATOR (used in nch)
        if h.title != "SKIP_LEGEND":
            self.histos.append(h)

    def add_histos(self, hs: List[histo]):
        """ Add list of histo to the legend """
        for h in hs:
            self.add_histo(h)

    def create_and_draw(self):
        """ Creates the legend from added histograms and draws

        Automatizes style (p/f/l)
        """
        self.yMin = self.yMax - self.height*len(self.histos)/self.nCol
        self.tlegend = TLegend(self.xMin, self.yMin, self.xMax, self.yMax)

        for h in self.histos:
            if h.inlegend is False:
                continue
            if "p" in h.drawoption:
                self.tlegend.AddEntry(h.th, h.title, "p")
            elif h.fillcolor:
                self.tlegend.AddEntry(h.th, h.title, "f")
            else:
                self.tlegend.AddEntry(h.th, h.title, "l")

        # TODO: config?
        self.tlegend.SetBorderSize(0)
        self.tlegend.SetFillStyle(0)
        self.tlegend.SetNColumns(self.nCol)
        self.tlegend.Draw()
