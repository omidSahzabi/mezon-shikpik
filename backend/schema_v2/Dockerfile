FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm
WORKDIR /app
COPY schema_v2/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /app
ENV DJANGO_SETTINGS_MODULE=schema_v2.settings
CMD ["python", "manage.py", "check"]
