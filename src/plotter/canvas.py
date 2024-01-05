from .pad import pad
import ROOT
from ROOT import TCanvas
from typing import Dict
import os
from .quiet import Quiet

import logging
log = logging.getLogger(__name__)


class canvas:
    """ Wrapper around TCanvas

    Automates few thinks which need to be done every time
    (e.g. drawin pads)
    """

    def __init__(self, name: str, x: int = 800, y: int = 800) -> None:
        """
        Arguments:
            name (``str``): name of canvas, used also as title
            x (``int``): x width of the canvas
            y (``int``): y width of the canvas
        """

        with Quiet(ROOT.kWarning+1):
            self.tcan = TCanvas(name, name, x, y)
        # TODO: still not 100% convinced we need a Dict and not just List
        self.pads: Dict[str, pad] = {}

        ROOT.gStyle.SetErrorX(0.5)

    def cd(self):
        """ cd() to the canvas
        """
        self.tcan.cd()

    def add_pad(self, p: "pad"):
        """ Adds pad to the canvas

        Arguments:
            p (``pad``): pad to be added to the canvas
        """
        self.pads[p.name] = p
        self.cd()
        p.tpad.Draw()

    def save(self, path: str):
        """ Calls SaveAs from TCanvas, creates dirs if necessary

        Arguments:
            path (``str``): path to target file
        """

        # if path contains directories, check if they exist
        # if not, create them
        if "/" in path:
            dirName = path[:path.rindex("/")]
            if not os.path.exists(dirName):
                log.info(f"Creating directory {dirName}")
                os.makedirs(dirName)

        # TODO: maybe add automatic saving with multiple suffixes or something?
        # printout not wanted, modify gErrorIgnoreLevel
        # TODO: create decorator if used more often
        oldIgnore = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = 3000
        self.tcan.SaveAs(path)
        ROOT.gErrorIgnoreLevel = oldIgnore

    def add_text(self, text: str, x: float, y: float, color: int = ROOT.kBlack):
        """ Adds text to the canvas at x,y position
        Arguments:
            text (``str``): text to be displayed
            x (``int``): x coordinate on the canvas (fraction)
            y (``int``): y coordinate on the canvas (fraction)
            color (``int``): ROOT TColor of the text, black by default
        """
        self.cd()
        ltx = ROOT.TLatex()
        ltx.SetNDC()
        ltx.SetTextColor(color)
        ltx.DrawLatex(x, y, text)
