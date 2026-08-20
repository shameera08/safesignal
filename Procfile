web: daphne -b 0.0.0.0 -p $PORT safesignal.asgi:application
worker: celery -A safesignal worker -l info --concurrency=2 --pool=solo
