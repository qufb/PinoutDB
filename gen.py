#!/usr/bin/env python3

from bs4 import BeautifulSoup
from pathlib import Path
import json
import re


def get_reference_name(aliases):
    for alias in aliases:
        if "(" not in alias:
            return alias
    return aliases[0]


id_aliases = dict()
with Path("out/id_aliases.json").open() as f:
    entries = json.load(f)
    for entry in entries:
        id_aliases[entry["@pin_map"]] = entry["@name"]

doc = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="/css/main.css" rel="stylesheet">
    </head>
    <body>
    </body>
</html>
"""

paths = Path("pinout").glob("*")
for path in paths:
    pinout_id = path.name
    if pinout_id not in id_aliases:
        continue

    soup = BeautifulSoup(
        doc,
        features="html.parser",
        preserve_whitespace_tags=["title", "h1", "th", "td"],
    )

    aliases = id_aliases[pinout_id].split(",")
    reference_name = get_reference_name(aliases)
    other_names = ", ".join([alias for alias in aliases if alias != reference_name])
    soup.html.head.append(soup.new_tag("title", string=pinout_id))
    soup.html.body.append(soup.new_tag("h1", string=reference_name))
    soup.html.body.append(soup.new_tag("p", string=f"Also matches: {other_names}"))

    table = soup.new_tag("table", attrs={"data-pagefind-body": None})
    th = soup.new_tag("th", string=f"Pin#")
    tr = soup.new_tag("tr")
    tr.append(th)
    table.append(tr)

    with path.open() as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            pins = [line.strip()]
            gnd_aliases = ["GND", "VSS"]
            for gnd_alias in gnd_aliases:
                if pins[0] == gnd_alias:
                    pins = gnd_aliases
                    break
            vcc_aliases = ["VCC", "VDD"]
            for vcc_alias in vcc_aliases:
                if pins[0] == vcc_alias:
                    pins = vcc_aliases
                    break
            data_match = re.search(r"^[DQ]Q?([0-9]+)(/A-1)?$", pins[0])
            if data_match:
                pins = [f"D{data_match.group(1)}{data_match.group(2) if data_match.group(2) else ''}"]

            pins_expanded = f"{i+1:>2}:{pins[0]}"
            if len(pins) > 1:
                pins_expanded += ' (' + ', '.join(f"{i+1:>2}:{pin}" for pin in pins[1:]) + ')'
            td = soup.new_tag("td", string=pins_expanded)
            tr = soup.new_tag("tr")
            tr.append(td)
            table.append(tr)
        soup.html.body.h1.attrs = {"data-pagefind-filter": f"pin_count:{len(lines)}"}

    soup.html.body.append(table)

    out_filename = Path("public") / f"{pinout_id}.html"
    with open(out_filename, "w") as f:
        f.write(soup.prettify(formatter=None))
