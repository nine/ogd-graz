#!/bin/bash

# Usage info
show_help() {
cat << EOF
Usage: ${0##*/} [-hv] -z ZOOM
Upscale tiles in TMS directory structure

    -h        display this help and exit
    -z ZOOM   zoom level corresponding to tile-directory, e.g. 12
    -v        verbose mode. Can be used multiple times for increased
              verbosity.
EOF
}

zoom=19
verbose=0

OPTIND=1 # Reset is necessary if getopts was used previously in the script.  It is a good idea to make this local in a function.
while getopts "hz:" opt; do
  case "$opt" in
    h)
        show_help
        exit 0
        ;;
    v)  verbose=$((verbose+1))
        ;;
    z)  zoom=$OPTARG
        ;;
    '?')
        show_help >&2
        exit 1
        ;;
  esac
done
shift "$((OPTIND-1))" # Shift off the options and optional --.


for f in $(find ./$((zoom))/ -type f -name '*.png')
do
  echo $f;
  y=$(basename $f | sed 's/\.png$//g')
  x=$(basename $(dirname $f))
  mkdir -p "./$((zoom+1))/$((2*x))"
  mkdir -p "./$((zoom+1))/$((2*x+1))"
  convert -size 256x256 $f -resize 512x512 \
    \( +clone -crop 256x256+0+0      +repage +adjoin -write "./$((zoom+1))/$((2*x))/$((2*y)).png"     +delete \) \
    \( +clone -crop 256x256+256+0    +repage +adjoin -write "./$((zoom+1))/$((2*x+1))/$((2*y)).png"   +delete \) \
    \( +clone -crop 256x256+0+256    +repage +adjoin -write "./$((zoom+1))/$((2*x))/$((2*y+1)).png"   +delete \) \
              -crop 256x256+256+256  +repage +adjoin        "./$((zoom+1))/$((2*x+1))/$((2*y+1)).png"
done


#eof
