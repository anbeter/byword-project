FROM python:3.11

ENV PYTHONPATH=/apps

WORKDIR /apps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]