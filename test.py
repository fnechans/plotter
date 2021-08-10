from plotter import collection, dataset, histo, pad, canvas, atlas, legend
import ROOT

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)

atlas.SetAtlasStyle()
ROOT.gStyle.SetErrorX(0.5)

cData = collection("Data", 1)
cData.add_dataset(dataset("Data", "test/Nominal/data.root", 1))

cBkg = collection("Bkg", 1)
cBkg.add_dataset(dataset("Bkg", "test/Nominal/background.root", 1))

hD = histo("Data", cData.get_th("ptll_data"), option="ep0x")
hB = histo("Top+EW", cBkg.get_th("ptll_topew"), fillColor=ROOT.kRed)
hB.th.SetMarkerSize(0)

c = canvas("canvas")

p = pad("main", yl=0.4)
c.add_pad(p)
p.add_histos([hD, hB])
p.set_title("p_{T}^{ll}", "Events")
p.logx()
p.logy()
p.margins(down=0)
p.plot_histos()
#p.tpad.BuildLegend()


#hR = hB.get_ratio(hD, fillToLine=True)
hR = hB.get_ratio(hB)
hR.set_fillColor(ROOT.kGray+1)
hR.set_lineColor(ROOT.kGray+1)
hR.th.SetFillStyle(3154);         
hR.th.SetLineStyle(3);
hR.option = "e2"

pR = pad("ratio", yh=0.4)
c.add_pad(pR)
pR.set_yrange(0.701, 1.299)
pR.add_histo(hR)
pR.logx()
pR.set_title("p_{T}^{ll}", "Ratio")
pR.margins(up=0)
pR.plot_histos()

c.tcan.cd()
atlas.ATLASLabel( 0.22, 0.92, "Internal" )

l = legend()
l.add_histos([hD, hB])
l.create_and_draw()

c.save("test/ptll.png")
