#!/usr/bin/env python
# -*- coding: utf-8 -*-

#try:
import mapnik2 as mapnik
#except:
#   import mapnik

import sys, os

# Set up projections
# spherical mercator (most common target map projection of osm data imported with osm2pgsql)
merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')

# long/lat in degrees, aka ESPG:4326 and "WGS 84" 
longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
# can also be constructed as:
#longlat = mapnik.Projection('+init=epsg:4326')

# ensure minimum mapnik version
if not hasattr(mapnik,'mapnik_version') and not mapnik.mapnik_version() >= 600:
    raise SystemExit('This script requires Mapnik >=0.6.0)')

print "Mapnik Version: ",mapnik.mapnik_version(),"\n"

if __name__ == "__main__":
    try:
        mapfile = os.environ['MAPNIK_MAP_FILE']
    except KeyError:
        mapfile = "osm.xml"
    
    map_uri = "image.png"

    #---------------------------------------------------
    #  Change this to the bounding box you want
    #
    bounds = (9.83, 53.46, 10.1, 53.62)
    #---------------------------------------------------
    bbox = mapnik.Box2d(*bounds)

    # Our bounds above are in long/lat, but our map
    # is in spherical mercator, so we need to transform
    # the bounding box to mercator to properly position
    # the Map when we call `zoom_to_box()`
    transform = mapnik.ProjTransform(longlat,merc)
    merc_bbox = transform.forward(bbox)
    print  merc_bbox.width(), merc_bbox.height(); 
    dpi=300	
    # 4cm auf der Karte sind 1km in der Natur ; 1km=1000m=100000cm; 4/10000
    massstab=4.0/100000.0 # 1cm
    # Punkte=( Breite auf der Karte in cm      )/2.54*dpi  
    #        ((Breite Natur in cm     )*massstab))/2.54*dpi
    #        ((merc_bbox.width()*10)*4/100000)/2.54*dpi     
    # Breite/Höhe in cm
    print ((merc_bbox.width()*100)*massstab)
    print ((merc_bbox.height()*100)*massstab)
    # Breite/Höhe in Punkten
    print ((merc_bbox.width()*100)*massstab)/2.54*dpi 
    print ((merc_bbox.height()*100)*massstab)/2.54*dpi    
    #
    imgx = int(((merc_bbox.width()*100)*massstab)/2.54*dpi)
    imgy = int(((merc_bbox.height()*100)*massstab)/2.54*dpi)
    #53.4948
    #9.7 rechts
    #53.43 unten
    #53.67 oben
    #10.2 links
    #m = mapnik.Map(600,300)
    m = mapnik.Map(imgx,imgy)
    mapnik.load_map(m,"stylefile.xml")
    
    # ensure the target map projection is mercator
    m.srs = merc.params()

    # Mapnik internally will fix the aspect ratio of the bounding box
    # to match the aspect ratio of the target image width and height
    # This behavior is controlled by setting the `m.aspect_fix_mode`
    # and defaults to GROW_BBOX, but you can also change it to alter
    # the target image size by setting aspect_fix_mode to GROW_CANVAS
    m.aspect_fix_mode = m.aspect_fix_mode.GROW_CANVAS
    # Note: aspect_fix_mode is only available in Mapnik >= 0.6.0
    # merc_bbox=(mapnik.Envelope( 1095383,7066673,1103176,7074154))
    #merc_bbox=  (mapnik.Envelope( 1079799,7062935,1135458,7107904))
    #proj +to +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over
    # 9.83 53.46
    # 10.1 53.62
    # 1094270.59      7068542.91
    # 1124326.86      7098514.81
    #merc_bbox= (mapnik.Box2d( 1094270,7068542,1124326,7098514))
    m.zoom_to_box(merc_bbox)
    #m.zoom_all()
    #imgx=zielgroeze_in_cm/2.54*dpi
    # render the map to an image
    #im = mapnik.Image(imgx,imgy)
    #mapnik.render(m, im)
    #im.save(map_uri,'png')
    
    sys.stdout.write('output image to %s!\n' % map_uri)
    
    # Note: instead of creating an image, rendering to it, and then 
    # saving, we can also do this in one step like:
    # mapnik.render_to_file(m, map_uri,'pdf')
    
    # And in Mapnik >= 0.7.0 you can also use `render_to_file()` to output
    # to Cairo supported formats if you have Mapnik built with Cairo support
    # For example, to render to pdf or svg do:
    mapnik.render_to_file(m, "image.pdf")
    mapnik.render_to_file(m, "image.svg")
    

