# Webserver
import random
import time

import numpy as np
from flask import Flask, Response
from flask_restx import Resource, Api, reqparse
import xml.etree.ElementTree as ET

# Instantiate flask app and corresponding REST Api
app = Flask(__name__)

api = Api(app,
          default='FieldView Karel API',
          default_label='An API to fetch FieldView Data from Karel programs',
          default_mediatype='application/xml',
          # prefix API calls
          prefix='/fieldview',
          # keep doc on root url
          doc='/')

PO_KEY = "obj"
PP_KEY = "pp"

PO_LIST_KEY = "obj_list"
PP_LIST_KEY = "pp_list"


PO_QUALITY_KEYS = ["bb_x", "bb_y"]
PP_QUALITY_KEYS = ["rot_diff", "dist"]

error_response = Response(ET.tostring(ET.Element("error"), encoding="ascii", method="xml"), mimetype='text/xml')

fake_target_points = [np.array([600, -300, 300, -170, -50, 0]), np.array([600, -300, 700, -170, -50, -50])]
current_idx = 0


class PickingObject:
    def __init__(self, object_id, position_2d: np.ndarray, quality: np.ndarray):
        self.object_id = str(object_id)
        self.x = float(position_2d[0])
        self.y = float(position_2d[1])
        self.quality = quality

    def generate_xml_params(self):
        params = {'id': self.object_id,
                  'x': str(self.x),
                  'y': str(self.y)
                  }
        n_quality = min(len(PO_QUALITY_KEYS), len(self.quality))
        for i in range(n_quality):
            params[PO_QUALITY_KEYS[i]] = str(self.quality[i])
        return params

    def add_to_xml(self, parent):
        ET.SubElement(parent, PO_KEY, self.generate_xml_params())


class PickingPoint:
    def __init__(self, picking_point_id, pose_6d: np.ndarray, quality: np.ndarray):
        self.picking_point_id = str(picking_point_id)
        self.x = float(pose_6d[0])
        self.y = float(pose_6d[1])
        self.z = float(pose_6d[2])
        self.w = float(pose_6d[3])
        self.p = float(pose_6d[4])
        self.r = float(pose_6d[5])
        self.quality = quality

    def generate_xml_params(self):
        params = {'id': self.picking_point_id,
                  'x': str(self.x),
                  'y': str(self.y),
                  'z': str(self.z),
                  'w': str(self.w),
                  'p': str(self.p),
                  'r': str(self.r)}
        n_quality = min(len(PP_QUALITY_KEYS), len(self.quality))
        for i in range(n_quality):
            params[PP_QUALITY_KEYS[i]] = str(self.quality[i])
        return params

    def add_to_xml(self, parent):
        ET.SubElement(parent, PP_KEY, self.generate_xml_params())

    def make_xml(self):
        return ET.Element(PP_KEY, self.generate_xml_params())


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

def calc_distance(*, current, target):
    distance = 0

    # check if same dimensions
    if len(current) == 3 and len(target) == 3:
        return np.linalg.norm(np.array(target)-np.array(current))

    return distance


# --------------------------------------------------------------------------

@api.route('/objects')
class ObjectsEndpoint(Resource):
    # HTTP GET
    def get(self):

        pos_2d = np.array([2, 1])
        bounding_box = np.array([1,1])

        objects = [PickingObject(str(i), pos_2d, bounding_box) for i in range(5)]

        return Response(serialize_picking_objects_xml(objects), mimetype='application/xml')

# --------------------------------------------------------------------------

@api.route('/picking-points')
class PickingPointsEndpoint(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('obj_id', type=str, required=True, help='ID of object for which picking points should be provided')
    parser.add_argument('relative', type=int, required=True, help='{0,1} Flag to decide on relative/absolute position')
    parser.add_argument('x', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('y', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('z', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('w', type=float, help='TCP Orientation (assumed 0 if missing)')
    parser.add_argument('p', type=float, help='TCP Orientation (assumed 0 if missing)')
    parser.add_argument('r', type=float, help='TCP Orientation (assumed 0 if missing)')

    # HTTP GET
    @api.expect(parser)
    def get(self):
        global fake_target_points
        global current_idx

        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('obj_id', type=str, required=True)
        parser.add_argument('relative', type=int, required=True)
        parser.add_argument('x', type=float)
        parser.add_argument('y', type=float)
        parser.add_argument('z', type=float)
        parser.add_argument('w', type=float)
        parser.add_argument('p', type=float)
        parser.add_argument('r', type=float)
        args = parser.parse_args()

        # new target each pp call

        if current_idx == 0:
            current_idx = 1
        else:
            current_idx = 0

        pose_6d = fake_target_points[current_idx]

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
        distance = calc_distance(current=pose_6d[:3], target=offset_6d[:3])
        corrected_pose_6d = pose_6d - offset_6d

        pps = [PickingPoint(str(i), corrected_pose_6d, [rotation_delta, distance]) for i in range(5)]

        return Response(serialize_picking_points_xml(pps), mimetype='application/xml')

# --------------------------------------------------------------------------

@api.route('/track-picking-point')
class TrackPickingPointEndpoint(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('pp_id', type=str, required=True, help='ID of picking point that should be tracked')
    parser.add_argument('relative', type=int, required=True, help='{0,1} Flag to decide on relative/absolute position')
    parser.add_argument('x', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('y', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('z', type=float, help='TCP Position (assumed 0 if missing)')
    parser.add_argument('w', type=float, help='TCP Orientation (assumed 0 if missing)')
    parser.add_argument('p', type=float, help='TCP Orientation (assumed 0 if missing)')
    parser.add_argument('r', type=float, help='TCP Orientation (assumed 0 if missing)')

    # HTTP GET
    @api.expect(parser)
    def get(self):
        global fake_target_points
        global current_idx
        # Parse arguments
        args = self.parser.parse_args()

        pose_6d = fake_target_points[current_idx]

        # simulate pose estimation jitter
        dist_scaling = 5
        rot_scaling = 5
        pose_6d[0] += (random.random() - 0.5) * dist_scaling
        pose_6d[1] += (random.random() - 0.5) * dist_scaling
        pose_6d[2] += (random.random() - 0.5) * dist_scaling
        pose_6d[3] += (random.random() - 0.5) * rot_scaling
        pose_6d[4] += (random.random() - 0.5) * rot_scaling
        pose_6d[5] += (random.random() - 0.5) * rot_scaling

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
        distance = calc_distance(current=pose_6d[:3], target=offset_6d[:3])
        corrected_pose_6d = pose_6d - offset_6d

        pp = PickingPoint(str(0), corrected_pose_6d, [rotation_delta, distance])

        return Response(ET.tostring(pp.make_xml(), encoding="ascii", method="xml"), mimetype='application/xml')
        #return error_response

if __name__ == '__main__':
    # Host on 0.0.0.0 (all local addresses)
    app.run(host='0.0.0.0', port=5000, debug=False)
