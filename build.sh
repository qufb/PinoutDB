#!/bin/sh

set -eu

mkdir -p ./dependencies ./out
test -f ./dependencies/infoic.xml \
  || wget 'https://gitlab.com/DavidGriffith/minipro/-/raw/c0c6972b2d0e80013a6bbde34f9dae0abbcb534c/infoic.xml?inline=false' -O ./dependencies/infoic.xml

test -f ./out/id_aliases.json \
  || xq '.infoic.database[].manufacturer[].ic[] | select(type == "object") | select(.["@type"] == "1")' ./dependencies/infoic.xml | jq -s '. | group_by([.["@pin_map"]]) | .[] | map({"@pin_map", "@name"}) | unique | reduce .[] as $x ({}; .["@name"] += "," + $x.["@name"] | .["@pin_map"] = $x.["@pin_map"]) | .["@name"] |= sub("^,"; "")' | jq -s . > ./out/id_aliases.json
