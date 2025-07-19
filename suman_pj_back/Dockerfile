FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/suman_pj_back

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]