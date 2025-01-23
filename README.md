# Introduction

# Usage

## Install prerequisites

### install packages

```shell
python3 -m pip install -r requirements.txt
```

```shell
sudo apt install poppler-utils tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra tesseract-ocr-chi-sim-vert tesseract-ocr-chi-tra-vert tesseract-ocr-script-hang-vert tesseract-ocr-script-hang tesseract-ocr-script-hans-vert tesseract-ocr-script-hans tesseract-ocr-script-hant-vert tesseract-ocr-script-hant
```

### Launch MinIO

```shell
docker run -d -p 9000:9000 -p 9001:9001 -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" -v ./minio:/data minio/minio server /data --console-address ":9001"
```

visit [minio adminstration website](http://localhost:9000). login with minioadmin:minioadmin.

create bucket references

### Launch Postgresql

```shell
docker pull postgres
docker run -e POSTGRES_DB=igs \
           -e POSTGRES_USER=igs \
           -e POSTGRES_PASSWORD=12345678 \
           -p 5432:5432 \
           --privileged --shm-size 12G -d postgres
```

create relations with the following command

```shell
psql -h localhost -U igs -d igs -a -f create_db.sql
```

## download references

```shell
python3 download.py --input_json pdf_list.json --minio_host <minio/host> --psql_host <psql/host>
```
