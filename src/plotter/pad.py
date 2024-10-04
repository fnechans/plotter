from . import loader
from .histo import histo
from . import thHelper
import ROOT
from ROOT import TPad
from typing import List, Dict, Optional, Any

import logging

log = logging.getLogger(__name__)


class pad:
    """Wrapper around TPad"""

    def __init__(
        self,
        name: str,
        xl: float = 0,
        xh: float = 1,
        yl: float = 0,
        yh: float = 1,
        isTH1: bool = True,
        configPath: str = loader.path() + "configs/pad.json",
        autoY=True,
    ) -> None:
        """
        Arguments:
            name (``str``): name of the pad
            xl (``int``): fraction of x-axis of the canvas the pad starts at
            xh (``int``): fraction of x-axis of the canvas the pad ends at
            yl (``int``): fraction of y-axis of the canvas the pad starts at
            yh (``int``): fraction of y-axis of the canvas the pad ends at
            isTH1 (``bool``): if true, advanced axis functions are used
            config (``str``): path to config of pad
            autoY (``bool``): if true, y-axis is autoscaled
        """
        self.tpad = TPad(name, name, xl, yl, xh, yh)
        self.name = name

        self.config: Dict[str, Any] = {}
        if configPath != "":
            self.config = loader.load_config(configPath)

        # if margins in config, update:
        if self.config is not {} and "margins" in self.config.keys():
            self.style_pad_margin(self.config["margins"])

        # for TH1 advanced axis functions are used
        self.isTH1 = isTH1

        self.histos: List[histo] = []
        self.xTitle: Optional[str] = None
        self.yTitle: Optional[str] = None

        self.yMin = 0.0
        self.yMinZero = 0.0  # for log, minimum >0
        self.yMax = 1.0
        self.xMin = 0.0
        self.xMax = 1.0
        # the logarithm of the y-axis is saved, as it affects the y-range
        self.isLogY = False
        # if user specifies y-range, we do not want to derive it automatically
        self.customYrange = False
        self.customXrange = False
        self.autoY = autoY

        self.basis: Optional[histo] = None

    def reset_histos(self) -> None:
        """Removes all histograms but keeps all non-histo settings"""
        self.histos = []
        self.customXrange = False
        self.customYrange = False
        self.basis = None

    def margins(
        self,
        up: Optional[float] = None,
        down: Optional[float] = None,
        left: Optional[float] = None,
        right: Optional[float] = None,
    ) -> None:
        """Set margins of the pad with default values,
        which work for the atlas style.

        Arguments:
            up (``float``): upper margin
            down (``float``): bottom margin
            left (``float``): left margin
            right (``float``): right margin
        """
        if up is not None:
            self.tpad.SetTopMargin(up)
        if down is not None:
            self.tpad.SetBottomMargin(down)
        if left is not None:
            self.tpad.SetLeftMargin(left)
        if right is not None:
            self.tpad.SetRightMargin(right)

    def logx(self, doLog: bool = True) -> None:
        """Sets the X-axis to log/lin

        Arguments:
            doLog (``bool``): if true, set logarithmic
        """
        self.tpad.SetLogx(doLog)

    def logy(self, doLog: bool = True) -> None:
        """Sets the Y-axis to log/lin

        Arguments:
            doLog (``bool``): if true, set logarithmic
        """
        if self.yMin < 0 or self.yMax < 0:
            log.warning("Histogram has negative values, skipping logy")
            return
        self.tpad.SetLogy(doLog)
        self.isLogY = doLog

        if self.basis is not None:
            if not self.customYrange and self.autoY:
                self._set_basis_yrange(margin=1.6)
            else:
                self._set_basis_yrange(margin=1)

    def add_histos(self, histos: List[histo]) -> None:
        """Adds list of histograms to the pad

        Arguments:
            histos (``List[hist]``): list of histos to be added
        """
        for h in histos:
            self.add_histo(h)

    def add_histo(self, h: histo) -> None:
        """Adds histogram to the pad and update min/max y value

        Arguments:
            h (``histo``): added histogram
        """
        self._update_range(h)
        self.histos.append(h)

    def update_range(self) -> None:

        for h in self.histos:
            self._update_range(h)

    def _update_range(self, h: histo) -> None:

        if h.isTH1:
            self._update_range_th1(h)
        elif h.isTGraph:
            self._update_range_tgraph(h)

    def _update_range_th1(
        self, h: histo
    ) -> None:  # TODO this function needs to take the xmin, xmax range into account!
        """Updates yMin/yMax if applicable for TH1"""

        if not self.customXrange:
            if self.histos == []:
                self.xMin = h.th.GetBinLowEdge(1)
                self.xMax = h.th.GetBinLowEdge(h.th.GetNbinsX() + 1)

        # if custom range defined, skip the automatic derivation
        if self.customYrange:
            return

        if self.histos == []:
            self.yMin = h.th.GetMinimum()
            self.yMinZero = h.th.GetMinimum(0)
            self.yMax = h.th.GetMaximum()
        else:
            if self.yMin > h.th.GetMinimum():
                self.yMin = h.th.GetMinimum()
            if self.yMinZero > h.th.GetMinimum(0):
                self.yMinZero = h.th.GetMinimum(0)
            if self.yMax < h.th.GetMaximum():
                self.yMax = h.th.GetMaximum()

    def _update_range_tgraph(self, h: histo) -> None:
        """Updates yMin/yMax if applicable for TH1"""

        # if custom range defined, skip the automatic derivation
        if self.customYrange:
            return

        if self.histos == []:
            self.yMin = thHelper.get_graph_minimum(h.th)
            self.yMax = thHelper.get_graph_maximum(h.th)
        else:
            cur_min = thHelper.get_graph_minimum(h.th)
            if self.yMin > cur_min:
                self.yMin = cur_min
            cur_max = thHelper.get_graph_maximum(h.th)
            if self.yMax < cur_max:
                self.yMax = cur_max

    def plot_histos(self) -> None:
        """Plots histograms, including creation of basis,
        which handles some properties of the plot,
        like the axis title or range
        """

        if len(self.histos) == 0:
            log.error("Pad does not contain any histograms!")
            # not sure that IndexError is the best one
            raise IndexError

        self.tpad.cd()
        # now lets clone the first histogram to manipulate axis and such
        # this is done because we do not want to modify any externally provided
        # histograms
        # TODO: add histo.clone??
        if self.histos[0].isTGraph:
            self.basis = histo(
                "",
                self.histos[0].th.Clone("basis").GetHistogram(),
                linecolor=ROOT.kWhite,
                fillcolor=ROOT.kWhite,
                drawoption="hist",
            )
        else:
            self.basis = histo(
                "",
                self.histos[0].th.Clone("basis"),
                linecolor=ROOT.kWhite,
                fillcolor=ROOT.kWhite,
                drawoption="hist",
            )
        self.basis.th.Reset()
        self._set_basis_axis_title()

        if self.customYrange:
            self._set_basis_yrange(margin=1)
        elif self.isTH1 and self.autoY:
            self._set_basis_yrange(margin=1.6)
        if self.customXrange or self.isTH1:
            self._set_basis_xrange()

        # if basis in config, update:
        if self.config is not {} and "basis" in self.config:
            self.style_pad_basis(self.config["basis"])

        self.basis.draw()

        for h in self.histos:
            h.draw(suffix=" same")

        self.basis.draw(drawoption="sameaxis")

    def _set_basis_axis_title(self) -> None:
        """Sets titles of the axis through the basis histogram"""
        if self.basis is None:
            log.error("Called basis function but no basis yet!")
            raise RuntimeError

        if self.xTitle:
            self.basis.th.GetXaxis().SetTitle(self.xTitle)
        if self.yTitle:
            self.basis.th.GetYaxis().SetTitle(self.yTitle)

    def set_title(
        self, xTitle: Optional[str] = None, yTitle: Optional[str] = None
    ) -> None:
        """Saves the axis titles, applies to the basis if already exists

        Arguments:
            xTitle (``str``): title of the x-axis
            yTitle (``str``): title of the y-axis
        """
        self.xTitle = xTitle
        self.yTitle = yTitle

        if self.basis is not None:
            self._set_basis_axis_title()

    def _set_basis_yrange(self, margin: float = 1.0) -> None:
        """Sets rangeof the y-axis through the basis histogram"""
        if self.basis is None:
            log.error("Called basis function but no basis yet!")
            raise RuntimeError

        # for the maximum you alway want to have some margin
        # TODO: margin as class variable?

        if not self.isLogY:
            self.basis.th.GetYaxis().SetRangeUser(self.yMin, self.yMax * margin)
        # for log it is little bit more complicated
        # but this usually ends up looking nice
        else:
            # Cannot do log if all values negative
            if self.yMax < 0:
                log.warning("Histogram has only negative values, cannot do log!")
            if self.yMax == 0:
                log.warning("Histogram max is 0, cannot do log!")
            else:
                fBot = 0.01  # little bit space on the bottom
                fPlot = (
                    1.0 / margin - fBot
                )  # plot takes 1/margin of the plot vertically
                fLeg = 1.0 - fPlot  # legend takes most of therest
                yMinLog = pow(self.yMinZero, (fPlot + fBot) / fPlot) / pow(
                    self.yMax, fBot / fPlot
                )
                yMaxLog = pow(self.yMax, (1.0 - fBot) / fPlot) / pow(
                    self.yMinZero, fLeg / fPlot
                )
                self.basis.th.GetYaxis().SetRangeUser(yMinLog, yMaxLog)

    def set_yrange(self, yMin: float = 0, yMax: float = 1) -> None:
        """Saves the y-axis range, applies to the basis if already exists

        Arguments:
            yMin (``float``): lower range of the y-axis
            yMax (``float``): upper range of the y-axis
        """
        self.yMin = yMin
        self.yMax = yMax
        self.customYrange = True

        if self.basis is not None and self.autoY:
            self._set_basis_yrange()

    def _set_basis_xrange(self) -> None:
        """Sets rangeof the x-axis through the basis histogram"""

        # only for setting both limits at the time for now TODO
        if not self.xMin and not self.xMax:
            return

        if self.basis is None:
            log.error("Called basis function but no basis yet!")
            raise RuntimeError

        self.basis.th.GetXaxis().SetRangeUser(self.xMin, self.xMax)

    def set_xrange(self, xMin: float = 0, xMax: float = 1) -> None:
        """Saves the x-axis range, applies to the basis if already exists

        Arguments:
            xMin (``float``): lower range of the x-axis
            xMax (``float``): upper range of the x-axis
        """
        self.xMin = xMin
        self.xMax = xMax
        self.customXrange = True

        if self.basis is not None:
            self._set_basis_xrange()

    def style_pad_margin(self, style: Dict[str, Any]) -> None:
        """Applies style to the pad margins

        Arguments:
            style (``Dict[str, Any]``): style config
        """

        log.debug("Updating margin style")

        for opt, set in style.items():
            if "margin_up" in opt:
                self.tpad.SetTopMargin(set)
            elif "margin_down" in opt:
                self.tpad.SetBottomMargin(set)
            elif "margin_left" in opt:
                self.tpad.SetLeftMargin(set)
            elif "margin_right" in opt:
                self.tpad.SetRightMargin(set)
            else:
                log.error(f"Unknown option {opt}")
                raise RuntimeError

    def style_pad_basis(self, style: Dict[str, Any]) -> None:
        """Applies style to the pad basis

        Arguments:
            style (``Dict[str, Any]``): style config
        """

        if self.basis is None:
            log.error("Called pad style but no basis yet!")
            raise RuntimeError
        log.debug("Updating basis style")

        for opt, set in style.items():
            self.update_style(opt, set)

    def update_style(self, opt: str, set: Any) -> None:
        """Update an option.

        Arguments:
            opt (``str``): option name
            set (``Any``): option value
        """
        if self.basis is None:
            log.error("Called pad style but no basis yet!")
            raise RuntimeError

        if "x_" in opt:
            axis = self.basis.th.GetXaxis()
            update_style_axis(axis, opt, set)
        elif "y_" in opt:
            axis = self.basis.th.GetYaxis()
            update_style_axis(axis, opt, set)
        elif "n_div" in opt:
            if len(set) != 2:
                log.error("n_div option in wrong format, need two items")
                raise RuntimeError
            if self.basis.isTH1:
                self.basis.th.SetNdivisions(set[0], set[1])
        else:
            log.error(f"Unknown option {opt}")
            raise RuntimeError


# STYLE HELPERS


def update_style_axis(axis, opt, set):
    """Update style of an axis

    Arguments:
        axis (``TAxis``): axis to update
        opt (``str``): option name
        set (``Any``): option value
    """
    if "titleOffset" in opt:
        axis.SetTitleOffset(set)
    elif "titleSize" in opt:
        axis.SetTitleSize(set)
    elif "titleFont" in opt:
        axis.SetTitleFont(set)
    elif "labelSize" in opt:
        axis.SetLabelSize(set)
    elif "labelFont" in opt:
        axis.SetLabelFont(set)
    else:
        log.error(f"Unknown option {opt}")
        raise RuntimeError
