from flask import Blueprint, jsonify, request
from src.models.world_model import WorldModel
from src.models.entity import Entity, EntityAttributeValue

api = Blueprint('api', __name__)
world_model = WorldModel(100)


@api.route('/api/register', methods=['POST'])
def register():
    data = request.json

    entity = Entity.from_dict(data)
    eavs = dict()
    for name, value in data['eav'].items():
        eav = EntityAttributeValue.from_dict({"entity_id": entity.id, "name": name, "value": value})
        eavs[eav.id] = eav

    response = world_model.register(entity.entity_type, entity.max_capacity, eavs)
    return jsonify(response, status=200, mimetype='application/json')


@api.route('/api/snapshot', methods=['GET'])
def snapshot():
    data = request.json
    response = world_model.snapshot(data['entity_id'])
    return jsonify(response.to_dict(), status=200, mimetype='application/json')


@api.route('/api/accept-person', methods=['POST'])
def accept_person():
    data = request.json
    response = world_model.accept_person(data['entity_id'], data['persons_id'])
    return jsonify({"occur": response}, status=200, mimetype='application/json')


@api.route('/api/service-done', methods=['POST'])
def service_done():
    data = request.json
    response = world_model.service_done(data['entity_id'], data['persons_id'])
    return jsonify({"occur": response}, status=200, mimetype='application/json')


@api.route('/api/update-self', methods=['PUT'])
def update_self():
    data = request.json
    response = world_model.update_self(data['entity_id'], data['max_capacity'], data['eavs'])
    return jsonify({"occur": response}, status=200, mimetype='application/json')


@api.route('/api/log', methods=['POST'])
def log():
    pass


@api.route('/api/person-injury', methods=['POST'])
def person_injury():
    data = request.json
    response = world_model.person_injury(data['entity_id'], data['persons_id'])
    return jsonify({"occur": response}, status=200, mimetype='application/json')


@api.route('/api/person-death', methods=['POST'])
def person_death():
    data = request.json
    response = world_model.person_death(data['entity_id'], data['persons_id'])
    return jsonify({"occur": response}, status=200, mimetype='application/json')
