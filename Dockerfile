FROM python:3.7

ENV DIR /opt/terminator
RUN mkdir $DIR

WORKDIR $DIR

COPY requirements.txt $DIR/
RUN pip install -r requirements.txt

COPY . $DIR/

EXPOSE 8000

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')"

CMD python3 manage.py runserver 0.0.0.0:8000
