import ROOT
from plotter import pdgRounding

def print_yields(hdata, hlistMC, ystr):
    ystr += "Process\t\t\tN_Entries\t\tIntegral\t\tUnderflow\t\tOverflow\n"

    hst_data = hdata.th
    ystr += hdata.title+"\t\t"+str(hst_data.GetEntries())+"\t\t"+str(hst_data.Integral())+"\t\t"+str(hst_data.GetBinContent(0))+"\t\t"+str(hst_data.GetBinContent(hst_data.GetNbinsX()+1))+"\n"

    for i in range(0,len(hlistMC)):
        hMC = hlistMC[i].th
        ystr += hlistMC[i].title+"\t\t"+str(hMC.GetEntries())+"\t\t"+str(hMC.Integral())+"\t\t"+str(hMC.GetBinContent(0))+"\t\t"+str(hMC.GetBinContent(hMC.GetNbinsX()+1))+"\n"

    return ystr

def print_yields_tex(title, hdata, hlistMC, ystr):
    s1, s2, s3, s4 = "", "", "", ""
    s1 = "\\documentclass{article}\n\\usepackage{array}\n\\usepackage{graphicx} % for \\resizebox\n\\begin{document}\n\\begin{table}[htbp]\n\\centering\n\\caption{"+title+"}\n\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{|c|c|c|c|c|}\n\\hline\nProcess & N\_Entries & Yield & Statistical unc. & Systematic unc.\\\\\n\\hline\n"
    hst_data = hdata.th
    entries = hst_data.GetEntries()
    err_entries = entries**0.5
    integral = hst_data.Integral()+hst_data.GetBinContent(0)+hst_data.GetBinContent(hst_data.GetNbinsX()+1)
    integral, err_entries = pdgRounding.pdgRound(integral, err_entries)

    s2 = str(hdata.title)+"&"+str(entries)+"&"+str(integral)+"&"+str(err_entries)+"&NA\\\\\n"
    for i in range(0,len(hlistMC)):
        hMC = hlistMC[i].th
        entries = hMC.GetEntries()
        err_entries = entries**0.5
        integral = hMC.Integral()+hMC.GetBinContent(0)+hMC.GetBinContent(hMC.GetNbinsX()+1)
        integral, err_entries = pdgRounding.pdgRound(integral, err_entries)

        s3 += f"{hlistMC[i].title}&{entries}&{integral}&{err_entries}&NA\\\\\n"
        
    s4 = "\\hline\n\\end{tabular}%\n}\\label{tab:"+title+"_yields_table}\n\\end{table}\n\\end{document}"

    ystr = s1+s2+s3+s4
    return ystr
