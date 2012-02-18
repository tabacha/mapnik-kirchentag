#!/usr/bin/python
import psycopg2
import re

def newCol(list):
	firstPointEq=list[9];
	a=list[5]
	b=list[6]
	print list[5];
	print list[6];
	print list[9];
	beg = re.compile( '(^LINESTRING\()')
	end = re.compile( '(\)$)')
	a=beg.sub("",a)
	a=end.sub("",a)
	b=beg.sub("",b)
	b=end.sub("",b)
	if (firstPointEq):
	   print "x"
	else:
	   print "LINESTRING("+b+","+",".join(a.split(",")[1:])+")"
	   

# Connect to an existing database
conn = psycopg2.connect("dbname=gis user=gisuser")

# Open a cursor to perform database operations
cur = conn.cursor()

cur.execute("DROP TABLE  IF EXISTS road_text;")

# Execute a command: this creates a new table
cur.execute("CREATE TABLE road_text (osm_id integer, way geometry, highway text,aeroway text,name text,ref text, length integer,bridge text);")
cur.execute("INSERT INTO road_text (select distinct osm_id,way,highway,aeroway,name,ref,char_length(ref) as length,                                                                                                       case when bridge in ('yes','true','1') then 'yes'::text else bridge end as bridge                                                                                from planet_osm_line                                                                                                                                             where waterway IS NULL                                                                                                                                             and leisure IS NULL                                                                                                                                              and landuse IS NULL                                                                                                                                              and (name is not  null or ref is not null));")

cur.execute("CREATE INDEX road_text_idx ON road_text USING GIST ( way );")
conn.commit()

cur.execute("SELECT a.osm_id,b.osm_id,a.name,a.highway,a.bridge,AsText(a.way),AsText(b.way),a.ref,b.ref,ST_Equals(ST_StartPoint(a.way),ST_StartPoint(b.way)) FROM road_text a, road_text b where a.name=b.name and a.highway=b.highway and NOT (a.osm_id=b.osm_id)  and a.bridge is NULL and b.bridge is NULL and ( ST_Equals(ST_StartPoint(a.way),ST_EndPoint(b.way)) or ST_Equals(ST_StartPoint(a.way),ST_StartPoint(b.way)));")
newCol(cur.fetchone());
newCol(cur.fetchone());
newCol(cur.fetchone());


cur.close()
conn.close()