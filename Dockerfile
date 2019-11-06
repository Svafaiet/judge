FROM python:3.7

ENV DIR /opt/terminator
RUN mkdir $DIR

WORKDIR $DIR

COPY requirements.txt $DIR/
RUN pip install -r requirements.txt

COPY . $DIR/

EXPOSE 8000

CMD python3 manage.py makemigrations
CMD python3 manage.py migrate
CMD python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"
CMD python3 manage.py runserver 0.0.0.0:8000
