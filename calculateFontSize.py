#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import re
import ImageFont

# Text Residential:
# Scale Denominator 7564 uebersicht Font: 16pt
# Scale Denominator 2389 Detail Font:18 pt (geändert auf 16pt)

# use a truetype font
font = ImageFont.truetype("../mapnik-2.0.0/fonts/dejavu-fonts-ttf-2.33/ttf/DejaVuSans.ttf", 16)


(width,height)=font.getsize("Neue Burg");
print "w: %d h: %d" % (width,height);
# Connect to an existing database
conn = psycopg2.connect("dbname=gis user=gisuser")

# Open a cursor to perform database operations
cur = conn.cursor()
# Neuer Wall ist 515 m lang, entspricht 1270 px in detailauflösung 451px in Uebersicht
# Uebersicht
ufactor=0.7
# Detail
dfactor=2.45
# Detail:
# In der Bash:
#  proj +to +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over
# 9.932 53.538
detminx=1105625.18
detminy=7083140.06
# 10.01 53.56
detmaxx=1114308.10
detmaxy=7087262.07
# Uebersicht
#9.83 53.46
uebminx=1094270.59
uebminy=7068542.91
#10.1 53.62
uebmaxx=1124326.86
uebmaxy=7098514.81

 #the_geom
 #    && SetSRID( 
 #    (
 #      SELECT ST_MakeBox3D(
 #        ST_GeomFromText( 'POINT( 9.932 53.538 )', 4326 ),
 #        ST_GeomFromText( 'POINT( 10.01 53.56 )', 4326 ) 
 #      )
 #     )::box3d,  900913)
 


infunc=" way && SetSRID( (SELECT ST_MakeBox3D(ST_GeomFromText('POINT( %d %d )', 900913 ),"
infunc=infunc+"ST_GeomFromText( 'POINT( %d %d )', 900913 ))),900913)";
indet=infunc%(detminx,detminy,detmaxx,detmaxy);
inueb=infunc%(uebminx,uebminy,uebmaxx,uebmaxy);
dsql="select w.name,MAX(ST_Length(w.way))/length(w.name) as platz ,MAX(ST_Length(w.way)) as max "
dsql=dsql+"FROM road_text w WHERE w.highway is not null AND w.name is not null  AND "+indet
dsql=dsql+" GROUP BY name ORDER BY platz;"

usql="select w.name,MAX(ST_Length(w.way))/length(w.name) as platz ,MAX(ST_Length(w.way)) as max "
usql=usql+"FROM road_text w WHERE w.highway is not null AND w.name is not null  AND "+inueb+" AND NOT ("+indet+")"
usql=usql+" GROUP BY name ORDER BY platz;"

cur.execute(usql);
res=cur.fetchall()

for row in res:
  (name,platz,way_len)=row;
  ulen=way_len*ufactor;
  dlen=way_len*dfactor;
  if name=="" or name==None:
    w=0
  else:
   (w,h)=font.getsize(name);
  if (w>ulen):
    print "%s\tnamelen=%d\tulen=%d" %(name,w,ulen)

cur.execute(dsql);
res=cur.fetchall()

print "---"
for row in res:
  (name,platz,way_len)=row;
  ulen=way_len*ufactor;
  dlen=way_len*dfactor;
  if name=="" or name==None:
    w=0
  else:
   (w,h)=font.getsize(name);
  if (w>dlen):
    print "%s\tnamelen=%d\tdlen=%d" %(name,w,dlen)

print "---"
conn.commit()
try:
 cur.execute("ALTER TABLE road_text ADD name1 varchar");
 conn.commit()
except psycopg2.ProgrammingError:
 conn.rollback()

cur.execute("select osm_id,name from road_text where name is not null");
res=cur.fetchall()
for row in res:
  (osm_id,name)=row
  name=name.replace("Straße","Str.")
  name=name.replace("straße","str.")
  name=name.replace("Brücke","Br.")
  name=name.replace("brücke","br.")
  name=name.replace("Chaussee","Ch.")
  name=name.replace("weg","w.")
  name=name.replace("Weg","W.")
  name=name.replace("damm","d.")
  name=name.replace("Damm","D.")
  name=name.replace("'","")
  
  cur.execute("UPDATE road_text SET name1='%s' WHERE osm_id='%d';" % (name,osm_id))

conn.commit()
cur.close()
conn.close()
