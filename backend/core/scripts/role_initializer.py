import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES_JSON_PATH = os.path.join(BASE_DIR, 'config', 'roles.json')


def ensure_roles_exist(db, Role):
    with open(ROLES_JSON_PATH, 'r') as f:
        required_roles = json.load(f)

    for role_id_str, role_name in required_roles.items():
        role_id = int(role_id_str)
        existing_role = Role.query.filter_by(role_id=role_id).first()
        if not existing_role:
            db.session.add(Role(role_id=role_id, role_name=role_name))

    db.session.commit()
