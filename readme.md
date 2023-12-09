# autojs-backend-server

1. 设备卡密生成及绑定

2. 设备自动分组实现负载均衡

# 使用

1. 构建镜像

   docker build -t fastapi -f api-Dockerfile .

2. 启动实例

   docker-compose -f api-compose.yml up

3. 查看 api 文档：

   http://127.0.0.1:80/docs## autojs-backend-server

## 启动所有服务

docker build -t moser -f moser-Dockerfile .

docker-compose -f mongo-compose.yml -f api-compose.yml up

## 内网穿透

docker-compose --env-file .env -f mongo-compose.yml -f api-compose.yml -f tunnel-compose.yml up
