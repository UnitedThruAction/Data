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
                 schema_types={},
                 map_name='Map', filename='~/Downloads/KMLWriter.kml'):
        """Generate KML from DataFrame."""

        kml = simplekml.Kml(name=map_name)

        if schema_types:
            schema = kml.newschema()
            for name, typ in schema_types.items():
                schema.newsimplefield(name=name, type=typ)

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
                obj = kml.newpolygon(name=name, description=description)
                obj.outerboundaryis = row[1].geometry.exterior.coords
            elif isinstance(row[1].geometry, shapely.geometry.multipolygon.MultiPolygon):
                obj = kml.newmultigeometry(name=name, description=description)
                for geom in row[1].geometry.geoms:
                    poly = obj.newpolygon()
                    poly.outerboundaryis = geom.exterior.coords

            obj.style.polystyle.color = color
            obj.style.polystyle.fill = 1
            obj.style.polystyle.outline = 0

            if schema_types:
                obj.extendeddata.schemadata.schemaurl = schema.id
                for name in schema_types:
                    obj.extendeddata.schemadata.newsimpledata(name, row[1][name])

        kml.save(path=filename)
        print('Saved {}'.format(filename))
