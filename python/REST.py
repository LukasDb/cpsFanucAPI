# Webserver
import time

import numpy as np
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

PO_QUALITY_KEY = "dist_2d"
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
                  PP_QUALITY_KEY: str(self.quality)}
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


def calc_degree_delta(*, alpha, beta):
    delta = abs(alpha - beta)
    return delta if delta < 180 else 360 - delta


def calc_rotation_delta(*, current, target):
    total_delta = 0

    # check if same dimensions
    if len(current) == len(target):
        # add all angle differences
        for i in range(len(current)):
            total_delta += calc_degree_delta(alpha=current[i], beta=target[i])

    return total_delta


# --------------------------------------------------------------------------

@api.route('/objects')
class ObjectsEndpoint(Resource):
    # HTTP GET
    def get(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        # TODO if params needed
        args = parser.parse_args()

        pos_2d = np.array([2, 1])
        distance = np.sqrt(np.square(pos_2d[0])+np.square(pos_2d[1]))

        objects = [PickingObject(pos_2d, distance) for i in range(5)]

        return Response(serialize_picking_objects_xml(objects), mimetype='text/xml')


# --------------------------------------------------------------------------

@api.route('/picking-points')
class PickingPointsEndpoint(Resource):
    # HTTP GET
    def get(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('relative', type=int)
        parser.add_argument('x', type=float)
        parser.add_argument('y', type=float)
        parser.add_argument('z', type=float)
        parser.add_argument('w', type=float)
        parser.add_argument('p', type=float)
        parser.add_argument('r', type=float)
        args = parser.parse_args()

        pose_6d = np.array([4.2, 7.8, 2.3, 45, 90, 180])
        offset_6d = np.array([0, 0, 0, 0, 0, 0])

        if args['relative']:
            # if parameter relative is set, the 6d parameters are assumed to be present
            offset_6d = np.array([
                args['x'],
                args['y'],
                args['z'],
                args['w'],
                args['p'],
                args['r']])

        rotation_delta = calc_rotation_delta(current=pose_6d[3:], target=offset_6d[3:])
        corrected_pose_6d = pose_6d - offset_6d

        pps = [PickingPoint(corrected_pose_6d, rotation_delta) for i in range(5)]

        return Response(serialize_picking_points_xml(pps), mimetype='text/xml')


# --------------------------------------------------------------------------

if __name__ == '__main__':
    # Host on 0.0.0.0 (all local addresses)
    app.run(host='0.0.0.0', port=5000, debug=False)
