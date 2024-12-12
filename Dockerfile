FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
ADD requirements.txt /
RUN pip install -r requirements.txt
WORKDIR /app
ADD . /app
RUN python3.10 -m pip install --upgrade pip
#ENTRYPOINT ["python3", "rentgen/manage.py", "runserver", "0.0.0.0:8080"]
#COPY .EasyOCR /root/.EasyOCR
#RUN rm -r /root/.EasyOCR
ENV EASYOCR_MODULE_PATH=/app/.EasyOCR
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
EXPOSE 8080
CMD ["python3", "rentgen/manage.py", "runserver", "0.0.0.0:8000"]