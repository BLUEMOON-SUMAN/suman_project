FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

RUN python /app/manage.py collectstatic --noinput

EXPOSE 8000

#  CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["gunicorn", "suman_pj_back.wsgi:application", "--bind", "0.0.0.0:$PORT"]