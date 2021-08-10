from ROOT import TStyle, TROOT
import ROOT

import logging
log = logging.getLogger(__name__)

ROOT.gROOT.SetBatch(True)

def SetAtlasStyle():
  atlasStyle = 0
  log.info("Applying ATLAS 2 style settings...")
  if atlasStyle==0:
    atlasStyle = AtlasStyle()
  ROOT.gROOT.SetStyle("ATLAS2")
  ROOT.gROOT.ForceStyle()


  ROOT.gStyle.SetErrorX(0.5)
#  return atlasStyle

def AtlasStyle():
  atlasStyle = TStyle("ATLAS2","Atlas style")

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
  atlasStyle.SetErrorX(0.5)
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

def ATLASLabel(x, y, text = "", color = ROOT.kBlack):
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