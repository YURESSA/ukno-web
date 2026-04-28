import json
import os

from sqlalchemy import func

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')


def ensure_data_exists(db, model, json_filename, id_field, name_field, keep_id=False):
    json_path = os.path.join(CONFIG_DIR, json_filename)
    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    for id_str, name in entries.items():
        entry_id = int(id_str)
        existing_entry = model.query.filter(
            (getattr(model, id_field) == entry_id) |
            (getattr(model, name_field) == name)
        ).first()
        if not existing_entry:
            data = {name_field: name}
            if keep_id:
                data[id_field] = entry_id
            db.session.add(model(**data))

    db.session.commit()

    if keep_id:
        seq_name = db.session.execute(
            f"SELECT pg_get_serial_sequence('{model.__tablename__}', '{id_field}')"
        ).scalar()
        max_id = db.session.query(func.max(getattr(model, id_field))).scalar() or 1
        db.session.execute(f"SELECT setval('{seq_name}', {max_id}, true)")
        db.session.commit()
