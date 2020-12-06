STORAGE=$(pwd)/files gunicorn --bind 0.0.0.0:5000 application:app
