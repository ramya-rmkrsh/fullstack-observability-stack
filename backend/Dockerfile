# backend Dockerfile
FROM python:3.11-alpine


RUN apk add --no-cache curl


# Set working directory
WORKDIR /app


# Copy application files to the container
COPY app.py /app/
COPY requirements.txt /app/
COPY gunicorn_config.py /app/

#EXPOSE 5057

# Install ddtrace for APM, Flask, and other dependencies in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install ddtrace
# Install Gunicorn to run the Flask app in production to enables spans in Datadog APM 
RUN pip install gunicorn  

# Run the script with ddtrace
#CMD ["python", "python-test.py"]
#CMD ["ddtrace-run", "python", "/app/app.py"]
# Use Gunicorn to use the gunicorn_config.py for log formatter and to enable spans in Datadog APM
CMD ["ddtrace-run", "gunicorn", "-b", "0.0.0.0:5000", "--config", "gunicorn_config.py", "app:app"]
