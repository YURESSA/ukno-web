import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')


def ensure_data_exists(db, model, json_filename, id_field, name_field):
    json_path = os.path.join(CONFIG_DIR, json_filename)
    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    for id_str, name in entries.items():
        entry_id = int(id_str)
        existing_entry = model.query.filter(getattr(model, id_field) == entry_id).first()
        if not existing_entry:
            db.session.add(model(**{
                id_field: entry_id,
                name_field: name
            }))

    db.session.commit()
