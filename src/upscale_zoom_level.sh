#!/bin/bash

zoom="20"

for f in $(find ./19/ -type f -name '*.png') 
do 
  echo $f;  
  y=$(basename $f | sed 's/\.png$//g')
  x=$(basename $(dirname $f))
  mkdir -p "./$zoom/$((2*x))"
  mkdir -p "./$zoom/$((2*x+1))"
  convert -size 256x256 $f -resize 512x512 \
    \( +clone -crop 256x256+0+0      +repage +adjoin -write "./$zoom/$((2*x))/$((2*y)).png"     +delete \) \
    \( +clone -crop 256x256+256+0    +repage +adjoin -write "./$zoom/$((2*x+1))/$((2*y)).png"   +delete \) \
    \( +clone -crop 256x256+0+256    +repage +adjoin -write "./$zoom/$((2*x))/$((2*y+1)).png"   +delete \) \
              -crop 256x256+256+256  +repage +adjoin        "./$zoom/$((2*x+1))/$((2*y+1)).png"
#  convert -size 256x256 $f -resize 512x512 -crop 256x256+0+0     +repage "../$zoom/$((2*x))/$((2*y)).png" 
#  convert -size 256x256 $f -resize 512x512 -crop 256x256+256+0   +repage "../$zoom/$((2*x+1))/$((2*y)).png"
#  convert -size 256x256 $f -resize 512x512 -crop 256x256+0+256   +repage "../$zoom/$((2*x))/$((2*y+1)).png"
#  convert -size 256x256 $f -resize 512x512 -crop 256x256+256+256 +repage "../$zoom/$((2*x+1))/$((2*y+1)).png"
done


#eof
