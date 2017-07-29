"""Convert a Geopandas dataframe of Polygons/MultiPolygons to KML for use in Google Maps.

@author n.o.franklin@gmail.com
@date 2017-07-29
"""

import simplekml
import shapely

class KMLWriter(object):
    """Convert a Geopandas dataframe of Polygons/MultiPolygons to KML for use in Google Maps."""

    def get_color_scale(self, color, scale):
        """Generate a color from a scale in the range 0..1 inclusive."""
        try:
            num = int(255 * (scale**2))
        except ValueError:
            num = 0
        return simplekml.Color.changealphaint(num, color)

    def generate(self, df, column_names, color=simplekml.Color.cornflowerblue,
                 map_name='Map', filename='~/Downloads/KMLWriter.kml'):
        """Generate KML from DataFrame."""

        kml = simplekml.Kml(name=map_name)
        for row in df.iterrows():
            if 'shape_name_column' in column_names:
                name = row[1][column_names['shape_name_column']].encode('ascii', 'ignore')
            else:
                name = None
            if 'description_column' in column_names:
                description = row[1][column_names['description_column']].encode('ascii', 'ignore')
            else:
                description = None
            if 'scale_column' in column_names:
                color = self.get_color_scale(color, row[1][column_names['scale_column']])
            else:
                color = self.get_color_scale(color, 0.5)

            if isinstance(row[1].geometry, shapely.geometry.polygon.Polygon):
                poly = kml.newpolygon(name=name, description=description)
                poly.outerboundaryis = row[1].geometry.exterior.coords
                poly.style.polystyle.color = color
                poly.style.polystyle.fill = 1
                poly.style.polystyle.outline = 1

            elif isinstance(row[1].geometry, shapely.geometry.multipolygon.MultiPolygon):
                multipnt = kml.newmultigeometry(name=name, description=description)
                for geom in row[1].geometry.geoms:
                    poly = multipnt.newpolygon()
                    poly.outerboundaryis = geom.exterior.coords
                multipnt.style.polystyle.color = color
                multipnt.style.polystyle.fill = 1
                multipnt.style.polystyle.outline = 1

        kml.save(path=filename)
        print('Saved {}'.format(filename))
