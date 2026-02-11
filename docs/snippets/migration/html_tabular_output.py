from eppy import readhtml

with open("eplustbl.htm") as f:
    html = f.read()
tables = readhtml.titletable(html)
