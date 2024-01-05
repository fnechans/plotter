from ROOT import TH1, TGraph
import ROOT
from array import array
from math import sqrt
from typing import List

import logging

log = logging.getLogger(__name__)

""" This file contains number of helper function for ROOT.TH1.

divide_ratio: divide function where error of the denominator
    is not takein into account.
"""


def divide_ratio(numTH: TH1, denTH: TH1) -> None:
    """For ratio, we do not to take into account
    errors of the denominator!

    Arguments:
        numTH (``TH1``): histogram to be divided
            (numerator, modified)
        denTH (``TH1``): histogram to be divided by
            (denominator, unchanged)
    """

    # TODO: check compability of histogram!
    # for now only bin number
    if numTH.GetNbinsX() != denTH.GetNbinsX():
        log.error("Incompatible histograms!")
        raise ValueError

    for i in range(numTH.GetNbinsX()):
        iBin = i + 1
        otherVal = denTH.GetBinContent(iBin)

        # to divide the value has to be non-zero:
        if otherVal:
            newVal = numTH.GetBinContent(iBin) / otherVal
            newErr = numTH.GetBinError(iBin) / otherVal
        # otherwise we set content to 0
        # TODO: issue a warning? debug?
        else:
            newVal = 0
            newErr = 0

        numTH.SetBinContent(iBin, newVal)
        numTH.SetBinError(iBin, newErr)


def rebin(TH: ROOT.TH1, binning: List[float], norm_by_width: bool = False) -> ROOT.TH1:
    """Returns rebinned copy of histogram based on provided binning.
    Only 1D for now
    Arguments:
        binning (``list``): list of bin edges
        norm_by_width (``bool``): whether to normalize by bin width
    """
    name = "Rebin" + TH.GetName()
    # Supress warning for replacing histogram
    ignore_level = ROOT.gErrorIgnoreLevel
    ROOT.gErrorIgnoreLevel = ROOT.kError
    reb_hist = ROOT.TH1D(name, name, len(binning) - 1, array('d', binning))
    ROOT.gErrorIgnoreLevel = ignore_level
    reb_hist.Sumw2()
    # check binning compatibility
    for n in range(reb_hist.GetNbinsX() + 1):
        new_edge = reb_hist.GetBinLowEdge(n + 1)
        found_edge = False
        for o in range(TH.GetNbinsX() + 1):
            oldEdge = TH.GetBinLowEdge(o + 1)
            epsilon = TH.GetBinWidth(o + 1) / 1000
            if abs(oldEdge - new_edge) < epsilon:
                found_edge = True
        if not found_edge:
            raise RuntimeError(
                'Provided binning does not match '
                'bins of the current histogram and rebinning is not possible! '
                'New bins have to be combinations of bins the original '
                'histogram.'
            )
    for old_bin in range(TH.GetNbinsX() + 2):
        new_bin = reb_hist.FindBin(TH.GetBinCenter(old_bin))
        reb_hist.SetBinContent(
            new_bin, TH.GetBinContent(old_bin) + reb_hist.GetBinContent(new_bin)
        )
        error = TH.GetBinError(old_bin) ** 2 + reb_hist.GetBinError(new_bin) ** 2
        reb_hist.SetBinError(new_bin, sqrt(error))
    if norm_by_width:
        reb_hist.Scale(1, "width")
    return reb_hist


def divide_ratio_graph(num: TGraph, den: TGraph) -> None:
    """ For ratio, we do not to take into account
    errors of the denominator!

    Arguments:
        numTH (``TGraph``): histogram to be divided
            (numerator, modified)
        denTH (``TGraph``): histogram to be divided by
            (denominator, unchanged)
    """
    size = min(num.GetN(), den.GetN())
    dRem = 0  # accounts for removed points (points where den=0)

    for i in range(size):
        errUp = 0
        errDo = 0
        val = 0
        denVal = den.GetY()[i-dRem]
        if denVal != 0:
            val = num.GetY()[i-dRem] / denVal
            if num.InheritsFrom("TGraphAsymmErrors"):
                errUp = num.GetErrorYhigh(i-dRem) / denVal
                errDo = num.GetErrorYlow(i-dRem) / denVal
            elif num.InheritsFrom("TGraphErrors"):
                errUp = num.GetErrorYhigh(i-dRem) / denVal
            num.SetPoint(i, num.GetX()[i-dRem], val)
            if num.InheritsFrom("TGraphAsymmErrors"):
                num.SetPointEYhigh(i-dRem, errUp)
                num.SetPointEYlow(i-dRem, errDo)
            elif num.InheritsFrom("TGraphErrors"):
                num.SetPointError(i, num.GetErrorXhigh(i-dRem), errUp)
        else:
            num.RemovePoint(i-dRem)
            dRem += 1


def get_graph_minimum(g: TGraph) -> float:
    """ Get minimum of a graph

    Arguments:
        g (``TGraph``):  target graph
    """
    if g.GetN() == 0:
        return -1111
    return min(g.GetY())


def get_graph_maximum(g: TGraph) -> float:
    """ Get minimum of a graph

    Arguments:
        g (``TGraph``):  target graph
    """
    if g.GetN() == 0:
        return -1111
    return max(g.GetY())
