FROM python:3.7

ENV DIR /opt/terminator
RUN mkdir $DIR

WORKDIR $DIR

COPY requirements.txt $DIR/
RUN pip install -r requirements.txt

COPY . $DIR/
