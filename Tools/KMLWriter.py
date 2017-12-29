"""Convert a Geopandas dataframe of Polygons/MultiPolygons to KML for use in Google Maps.

@author n.o.franklin@gmail.com
@date 2017-07-29
"""

import simplekml
import shapely
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def get_color_scale(color, scale):
    """Generate a color from a scale in the range 0..1 inclusive."""
    try:
        num = int(255 * (scale**2))
    except ValueError:
        num = 0
    return simplekml.Color.changealphaint(num, color)


def get_color_range(colormap, scale, alpha):
    """Get color from matplotlib colormap, in the range 0..1 inclusive.
    See https://matplotlib.org/users/colormaps.html.
    Specify alpha from 0..255."""
    cmap = plt.cm.get_cmap(colormap)
    try:
        num = int(cmap.N * scale)
    except ValueError:
        num = 0
    rgb = cmap(num)[:3]
    hexstring = colors.rgb2hex(rgb)
    hex_color = simplekml.Color.hex(hexstring[1:])
    return simplekml.Color.changealphaint(alpha, hex_color)


def generate(df, column_names, color_detail={},
             schema_types={},
             map_name='Map',
             outline=0,
             fill=1,
             filename='~/Downloads/KMLWriter.kml'):
    """Generate KML from DataFrame.  For example:
        KMLWriter.generate(df,
           column_names={'shape_name_column':'Name',
                         'description_column':'Description'},
           color_detail={'colormap':'PiYG',
                         'color_scale':'Scale',
                         'alpha': 200},
           schema_types={'Percent Democrats':'str'},
           map_name='Registered Democrats',
           filename='/Users/nick/Downloads/registered_dems.kml')
    """

    kml = simplekml.Kml(name=map_name)

    if schema_types:
        schema = kml.newschema()
        for name, typ in schema_types.items():
            schema.newsimplefield(name=name, type=typ)

    for row in df.iterrows():
        if 'shape_name_column' in column_names:
            name = str(row[1][
                column_names['shape_name_column']]).encode(
                'ascii', 'ignore')
        else:
            name = None

        if 'description_column' in column_names:
            description = str(row[1][
                column_names['description_column']]).encode(
                'ascii', 'ignore')
        else:
            description = None

        if isinstance(row[1].geometry, shapely.geometry.point.Point):
            obj = kml.newpoint(name=name, description=description,
                               coords=row[1].geometry.coords)
        elif isinstance(row[1].geometry, shapely.geometry.polygon.Polygon):
            obj = kml.newpolygon(name=name, description=description)
            obj.outerboundaryis = row[1].geometry.exterior.coords
        elif isinstance(row[1].geometry, shapely.geometry.multipolygon.MultiPolygon):
            obj = kml.newmultigeometry(name=name, description=description)
            for geom in row[1].geometry.geoms:
                poly = obj.newpolygon()
                poly.outerboundaryis = geom.exterior.coords
        else:
            continue  # skip rows without valid geometry

        if ('color' in color_detail) and ('color_scale' in color_detail):
            obj.style.polystyle.color = get_color_scale(
                color_detail['color'],
                row[1][color_detail['color_scale']])
        elif ('colormap' in color_detail) and ('color_scale' in color_detail) and ('alpha' in color_detail):
            obj.style.polystyle.color = get_color_range(
                color_detail['colormap'], row[1][color_detail['color_scale']], color_detail['alpha'])
        else:
            obj.style.polystyle.color = get_color_scale(
                simplekml.Color.cornflowerblue, 0.5)

        obj.style.polystyle.fill = fill
        obj.style.polystyle.outline = outline

        if schema_types:
            obj.extendeddata.schemadata.schemaurl = schema.id
            for name in schema_types:
                obj.extendeddata.schemadata.newsimpledata(
                    name, row[1][name])

    kml.save(path=filename)
    print('Saved {}'.format(filename))
