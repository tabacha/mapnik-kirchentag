#!/bin/bash
DATE=$(date +"%d.%m.%Y %H:%M:%S")
python gen-img.py
python gen-img.py ue
python gen-img.py ue-s
python gen-img.py de-s

DEST=s3://kirchentag.sven.anders.im/
s3cmd put detail.png detail.pdf detail.svg ${DEST}
s3cmd put detail-s.png detail-s.pdf detail-s.svg ${DEST}
s3cmd put uebersicht.png uebersicht.pdf uebersicht.svg  ${DEST}
s3cmd put uebersicht-s.png uebersicht-s.pdf uebersicht-s.svg  ${DEST}
sed -i -e "s/Stand:.*\$/Stand:$DATE/" index.html
s3cmd put index.html ${DEST}