# python ./manage.py makemigrations --noinput
 
python ./manage.py migrate --noinput

python manage.py collectstatic -c --noinput

gunicorn ticket_app.wsgi --bind 0.0.0.0:8000 --timeout 400