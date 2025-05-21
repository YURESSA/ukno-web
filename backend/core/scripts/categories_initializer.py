import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_JSON_PATH = os.path.join(BASE_DIR, 'config', 'categories.json')


def ensure_categories_exist(db, Category):
    with open(CATEGORIES_JSON_PATH, 'r') as f:
        required_categories = json.load(f)

    for category_name_str, category_name in required_categories.items():
        category_name = int(category_name_str)
        existing_category = Category.query.filter_by(category_name=category_name).first()
        if not existing_category:
            db.session.add(Category(category_name=category_name))

    db.session.commit()
