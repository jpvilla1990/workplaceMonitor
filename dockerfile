FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev pkg-config gcc g++ \
    libgl1-mesa-glx libgl1-mesa-dri \
    libglib2.0-0 libglib2.0-dev && \
    apt-get clean

RUN pip install \
    moviepy==1.0.3 \
    pims==0.6.1 \
    PyYAML==6.0 \
    Pillow==9.5.0 \
    pytest==7.4.0 \
    numpy==1.25.0rc1 \
    opencv-python==4.7.0.72 \
    mysql==0.0.3 \
    mysql-connector-python==8.1.0 \
    torch \
    torchvision \
    fastapi==0.97.0 \
    uvicorn==0.22.0 \
    psutil==5.9.5

#ENTRYPOINT ["uvicorn"]
#CMD ["main:app", "--host", "0.0.0.0", "--port", "80"]