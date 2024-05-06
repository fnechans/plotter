from plotter import pdgRounding


def print_yields_tex(title, hdata, hlistMC, ystr):
    s1, s2, s3, s4 = "", "", "", ""
    s1 = (
        r"\\documentclass{article}\n\\usepackage{array}\n\\usepackage{graphicx} % "
        r"for \\resizebox\n\\begin{document}\n\\begin{table}[htbp]\n\\centering\n\\caption{"
        + title
        + r"}\n\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{|c|c|c|c|c|}\n\\hline\nProcess "
          r"& N\_Entries & Yield & Statistical unc. & Systematic unc.\\\\\n\\hline\n"
    )
    hst_data = hdata.th
    entries = hst_data.GetEntries()
    err_entries = entries**0.5
    integral = hst_data.Integral(0, hst_data.GetNbinsX() + 1)
    err_entries = pdgRounding.pdgRoundData(
        integral, err_entries
    )  # not rounding data integral

    s2 = (
        str(hdata.title)
        + "&"
        + str(entries)
        + "&"
        + str(integral)
        + "&"
        + str(err_entries)
        + "&NA\\\\\n"
    )

    for i in range(0, len(hlistMC)):
        hMC = hlistMC[i].th
        entries = hMC.GetEntries()
        if entries == 0:
            frac_err_entries = 0
        else:
            frac_err_entries = (entries**0.5) / entries  # fractional error
        integral = hMC.Integral(0, hMC.GetNbinsX() + 1)
        err_entries = frac_err_entries * integral
        integral, err_entries = pdgRounding.pdgRound(integral, err_entries)

        s3 += f"{hlistMC[i].title}&{entries}&{integral}&{err_entries}&NA\\\\\n"

    s4 = (
        "\\hline\n\\end{tabular}%\n}\\label{tab:"
        + title
        + "_yields_table}\n\\end{table}\n\\end{document}"
    )

    ystr = s1 + s2 + s3 + s4
    return ystr
