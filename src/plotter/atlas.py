from ROOT import TStyle, TROOT
import ROOT
from typing import Dict

import logging
log = logging.getLogger(__name__)

ROOT.gROOT.SetBatch(True)

def SetAtlasStyle():
  atlasStyle = 0
  log.info("Applying ATL2 style settings...")
  if atlasStyle==0:
    atlasStyle = AtlasStyle()
  ROOT.gROOT.SetStyle("ATL2")
  ROOT.gROOT.ForceStyle()
#  return atlasStyle

def AtlasStyle():
  atlasStyle = TStyle("ATL2","Atlas style")

  # use plain black on white colors
  icol=0 # WHITE
  atlasStyle.SetFrameBorderMode(icol)
  atlasStyle.SetFrameFillColor(icol)
  atlasStyle.SetCanvasBorderMode(icol)
  atlasStyle.SetCanvasColor(icol)
  atlasStyle.SetPadBorderMode(icol)
  atlasStyle.SetPadColor(icol)
  atlasStyle.SetStatColor(icol)
  #atlasStyle->SetFillColor(icol); // don't use: white fill color for *all* objects

  # set the paper & margin sizes
  atlasStyle.SetPaperSize(20,26)

  # set margin sizes
  atlasStyle.SetPadTopMargin(0.05)
  atlasStyle.SetPadRightMargin(0.05)
  atlasStyle.SetPadBottomMargin(0.16)
  atlasStyle.SetPadLeftMargin(0.16)

  # set title offsets (for axis label)
  atlasStyle.SetTitleXOffset(1.2)
  atlasStyle.SetTitleYOffset(1.4)

  # use large fonts
  #font=72; // Helvetica italics
  font=42 # Helvetica
  tsize=0.06
  atlasStyle.SetTextFont(font)

  atlasStyle.SetTextSize(tsize)
  atlasStyle.SetLabelFont(font,"x")
  atlasStyle.SetTitleFont(font,"x")
  atlasStyle.SetLabelFont(font,"y")
  atlasStyle.SetTitleFont(font,"y")
  atlasStyle.SetLabelFont(font,"z")
  atlasStyle.SetTitleFont(font,"z")

  atlasStyle.SetLabelSize(tsize,"x")
  atlasStyle.SetTitleSize(tsize,"x")
  atlasStyle.SetLabelSize(tsize,"y")
  atlasStyle.SetTitleSize(tsize,"y")
  atlasStyle.SetLabelSize(tsize,"z")
  atlasStyle.SetTitleSize(tsize,"z")

  # use bold lines and markers
  atlasStyle.SetMarkerStyle(20)
  atlasStyle.SetMarkerSize(1.2)
  atlasStyle.SetHistLineWidth(2)
  atlasStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

  # get rid of X error bars (as recommended in ATLAS figure guidelines)
  # atlasStyle.SetErrorX(0.0001)
  # get rid of error bar caps
  atlasStyle.SetEndErrorSize(0.)

  # do not display any of the standard histogram decorations
  atlasStyle.SetOptTitle(0)
  #atlasStyle->SetOptStat(1111);
  atlasStyle.SetOptStat(0)
  #atlasStyle->SetOptFit(1111);
  atlasStyle.SetOptFit(0)

  # put tick marks on top and RHS of plots
  atlasStyle.SetPadTickX(1)
  atlasStyle.SetPadTickY(1)

  return atlasStyle

#SetAtlasStyle()

def ATLASLabel(x=0.22, y=0.9, text = "", color = ROOT.kBlack):
  l = ROOT.TLatex()
  l.SetNDC()
  l.SetTextFont(72)
  l.SetTextColor(color)
  delx = 0.115*696*ROOT.gPad.GetWh()/(472*ROOT.gPad.GetWw())
  l.DrawLatex(x,y,"ATLAS")
  if text:
    p = ROOT.TLatex()
    p.SetNDC()
    p.SetTextFont(42)
    p.SetTextColor(color)
    p.DrawLatex(x+delx,y,text)

def get_lumi() -> Dict[str, float]:
  luminosity = {}
  luminosity["mc16a"] = (32988.1+3219.56)
  luminosity["mc16d"] = 44307.4
  luminosity["mc16e"] = 58450.1
  return luminosity

def get_year2campaign() -> Dict[str, str]:
  year2campaign = {
    "": "", # all years = all campaigns
    "1516": ".mc16a",
    "17": ".mc16d",
    "18": ".mc16e",
  }
  return year2campaign

def recommended_colors():
  return [ROOT.kBlack, ROOT.kGreen, ROOT.kGreen + 2, ROOT.kRed,ROOT.kRed + 2, ROOT.kOrange, ROOT.kOrange + 2, ROOT.kBlue, ROOT.kBlue + 2, ROOT.kViolet, ROOT.kViolet + 2, ROOT.kPink, ROOT.kPink + 2]
