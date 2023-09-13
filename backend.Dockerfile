FROM python:3.11
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY foodcartapp foodcartapp
COPY places places
COPY restaurateur restaurateur
COPY star_burger star_burger
COPY templates templates
COPY manage.py manage.py

CMD ["gunicorn", "star_burger.wsgi:application", "--bind", "0:8000"]
