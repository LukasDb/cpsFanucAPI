# Webserver
from flask import Flask, Response
from flask_restx import Resource, Api, reqparse
import xml.etree.ElementTree as ET

# Instantiate flask app and corresponding REST Api
app = Flask(__name__)
api = Api(app)

PO_KEY = "obj"
PP_KEY = "pp"

PO_LIST_KEY = "obj_list"
PP_LIST_KEY = "pp_list"

PO_QUALITY_KEY = "dist"
PP_QUALITY_KEY = "rot_diff"

class PickingObject:
    def __init__(self, position_2d, quality):
        self.x = float(position_2d[0])
        self.y = float(position_2d[1])
        self.quality = quality

    def add_to_xml(self, parent):
        params = {'x': str(self.x),
                  'y': str(self.y),
                  PO_QUALITY_KEY: str(self.quality)}
        ET.SubElement(parent, PO_KEY, params)


class PickingPoint:
    def __init__(self, pose_6d, quality):
        self.x = float(pose_6d[0])
        self.y = float(pose_6d[1])
        self.z = float(pose_6d[2])
        self.w = float(pose_6d[3])
        self.p = float(pose_6d[4])
        self.r = float(pose_6d[5])
        self.quality = quality

    def add_to_xml(self, parent):
        params = {'x': str(self.x),
                  'y': str(self.y),
                  'z': str(self.z),
                  'w': str(self.w),
                  'p': str(self.p),
                  'r': str(self.r),
                  PP_QUALITY_KEY: str(self.quality),
                  }
        ET.SubElement(parent, PP_KEY, params)

def serialize_picking_objects_xml(picking_objects: [PickingObject]):
    root = ET.Element(PO_LIST_KEY)
    for po in picking_objects:
        po.add_to_xml(root)
    return ET.tostring(root, encoding="ascii", method="xml")


def serialize_picking_points_xml(picking_points: [PickingPoint]):
    root = ET.Element(PP_LIST_KEY)
    for pp in picking_points:
        pp.add_to_xml(root)
    return ET.tostring(root, encoding="ascii", method="xml")

def degree_delta(alpha, beta):
    delta = abs(alpha - beta)
    return (delta if delta < 180 else 360 - delta)


def rotation_delta(current, target):
    total_delta = 0

    # check if same dimensions
    if (len(current) != len(target)):
        # add all angle differences
        for i in current:
            total_delta += degree_delta(current[i], target[i])

    return total_delta

@api.route('/xml_endpoint')
class XMLEndpoint(Resource):
    def get(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('relative', type=bool)
        args = parser.parse_args()

        # Build response with flask function, default http code is 200 (OK)
        # response = make_response({"text": text})
        # Add header so Angular doesnt complain
        # response.headers.add("Access-Control-Allow-Origin", "*")
        # return response
        root = ET.Element('list_tag')
        for i in range(15):
            x = ET.SubElement(root, 'struct_tag', {'int_val': str(i), 'float_val': str(-3.5 + i),
                                                   'string_val': "abc" if i % 2 == 0 else "def"})

        return Response(ET.tostring(root, encoding="ascii", method="xml"), mimetype='text/xml')


# --------------------------------------------------------------------------

@api.route('/objects')
class XMLEndpoint(Resource):
    def get(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('obj-id', type=str)
        args = parser.parse_args()

        objects = [PickingObject([1.2, 3.4], 2.1) for i in range(5)]

        return Response(serialize_picking_objects_xml(objects), mimetype='text/xml')


# --------------------------------------------------------------------------

@api.route('/picking-points')
class XMLEndpoint(Resource):
    def get(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('relative', type=bool)
        args = parser.parse_args()

        pp = [PickingPoint([4.2, 7.8, 2.3, 45, 90, 180], 2.1) for i in range(5)]

        return Response(serialize_picking_points_xml(pp), mimetype='text/xml')


# --------------------------------------------------------------------------

if __name__ == '__main__':
    # Host on 0.0.0.0 (all local addresses)
    app.run(host='0.0.0.0', port=5000, debug=False)



