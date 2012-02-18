#!/usr/bin/python
import psycopg2
import re

def newCol(cur,list):
	firstPointEq=list[4];

	b=list[3]
	#print "---\n"
	print "Combi ",list[0],"+",list[1]
	#print "2",list[2]
	#print "3",list[3]
	#print "5",list[5]
	beg = re.compile( '(^LINESTRING\()')
	end = re.compile( '(\)$)')
	b=beg.sub("",b)
	b=end.sub("",b)
	lstr=""
	if (firstPointEq):
	   a=list[5];
           a=beg.sub("",a)
	   a=end.sub("",a)
	   lstr="LINESTRING("+a+","+",".join(b.split(",")[1:])+")"
	else:
	   a=list[2]
	   a=beg.sub("",a)
	   a=end.sub("",a)
	   lstr="LINESTRING("+b+","+",".join(a.split(",")[1:])+")"
	cur.execute("UPDATE road_text SET way=GeometryFromText('%s',900913) WHERE osm_id='%d';" % (lstr,list[0]))
	cur.execute("DELETE FROM road_text WHERE osm_id='%d';" % list[1])


# Connect to an existing database
conn = psycopg2.connect("dbname=gis user=gisuser")

# Open a cursor to perform database operations
cur = conn.cursor()

cur.execute("DROP TABLE  IF EXISTS road_text;")

# Execute a command: this creates a new table
cur.execute("CREATE TABLE road_text (osm_id integer, way geometry, highway text,aeroway text,name text,ref text, length integer,bridge text);")
cur.execute("INSERT INTO road_text (select distinct osm_id,way,highway,aeroway,name,ref,char_length(ref) as length,                                                                                                       case when bridge in ('yes','true','1') then 'yes'::text else bridge end as bridge                                                                                from planet_osm_line                                                                                                                                             where waterway IS NULL                                                                                                                                             and leisure IS NULL                                                                                                                                              and landuse IS NULL                                                                                                                                              and (name is not  null or ref is not null));")

#INSERT INTO geometry_columns(f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, "type")
#SELECT '', 'public', 'vwmytablemercator', 'the_geom', ST_CoordDim(the_geom), ST_SRID(the_geom), GeometryType(the_geom)
#FROM public.vwmytablemercator LIMIT 1;

cur.execute("delete from geometry_columns where f_table_name='road_text';")
cur.execute("INSERT INTO  geometry_columns(f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, \"type\") SELECT '', 'public', 'road_text', 'way', ST_CoordDim(way), ST_SRID(way), GeometryType(way) FROM public.road_text LIMIT 1;")
cur.execute("CREATE INDEX road_text_idx ON road_text USING GIST ( way );")
conn.commit()
res=1
while (res != None):
  #                   0            1      2              3              4                                               5
  cur.execute("SELECT a.osm_id,b.osm_id,AsText(a.way),AsText(b.way),ST_Equals(ST_StartPoint(a.way),ST_StartPoint(b.way)),AsText(ST_Reverse(a.way)) FROM road_text a, road_text b WHERE a.name=b.name and a.highway=b.highway and NOT (a.osm_id=b.osm_id)  and a.bridge is NULL and b.bridge is NULL and ( ST_Equals(ST_StartPoint(a.way),ST_EndPoint(b.way)) or ST_Equals(ST_StartPoint(a.way),ST_StartPoint(b.way))) LIMIT 1")
  res=cur.fetchone();
  if (res != None):
    newCol(cur,res);
    conn.commit()


cur.close()
conn.close()