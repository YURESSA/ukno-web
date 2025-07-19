import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from backend.app import register_static_routes
from backend.core import create_app
from backend.core.scripts.clear_unpaid import cleanup_unpaid_reservations

app = create_app()
register_static_routes(app)


def run_cleanup():
    with app.app_context():
        cleanup_unpaid_reservations()


scheduler = BackgroundScheduler()
scheduler.add_job(run_cleanup, 'interval', minutes=15, max_instances=120)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run()
