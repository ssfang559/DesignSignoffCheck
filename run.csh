#!/bin/csh -f

set design_signoff_check = "/apps/imctf/cad/script/DesignSignoffCheck/Other/Latest/DesignSignoffCheck.py "

${design_signoff_check} -calibre "2020.1_36.18" \
                        -project "drcot" \
                        -libName "10G5_16GDDR5_TV_BT00_DLT00_20230406" \
                        -cellName "TV_FULL_10G5P" \
                        -preVersion "TV_REV04" \
                        -version "TV" \
                        -rerun

