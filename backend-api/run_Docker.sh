cp ../requirements.txt ./
docker build -t backend-api:latest .
docker run -d -p 5000:5000 --name backend-api-container backend-api:latest


docker ps -a
docker stop backend-api-container
docker rm backend-api-container

docker run -d -p 5000:5000 --name backend-api-container -e MODE=docker backend-api:latest
