#!/bin/bash

find . -type f -print0 | xargs -0 file -i | grep -i html|grep -oE "^([.]|[^:]*)" | xargs -d \\n rm
