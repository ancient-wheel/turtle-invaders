FROM python:3.12-slim
RUN apt update && apt install -y python3-tk
WORKDIR /app/
COPY . .
CMD [ "python3", "main.py" ]