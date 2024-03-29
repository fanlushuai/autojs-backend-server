# autojs-backend-server

目标构建用于适合快速实现 autojs 简单服务的后端系统。技术选型上面，考虑的就是尽量简单。**以不写一行代码为荣。**

使用基于 http 的 mongodb，对接 autojs 简直不要太随意。不用写一行代码，就能实现，基本的数据结构随便操作。类似表操作。

使用基于 http 的 redis，对接 autojs 简直不要太随意。各种操作全部暴露给前端，前端封装 htpp 操作 redis 指令，快速直接的操作 redis

使用基于 python，快速构建，简单的 api。简直不要太随意。

使用 docker compose 自动部署，简直不要太 ok。

使用 caddy ，对各种服务进行路由转发，路由重写，自动 https,数据安全。基本认证。统一路由，统一搞认证。

使用，tunnel，进行内网穿透，简直不要太方便。测试期间。服务器不用买了。

## 基本架构

```mermaid
    graph LR
    A[tunnel]--->B[caddy]

    B[caddy]--->api[api]
    B[caddy]--->D[mongdb]

    api[api]--->mysql[mysql]

    a(navicat)--->mysql[mysql]
    a(navicat)--->D[mongdb]

```

- api 服务：承担需要持久化的数据内容以及一些逻辑判断的功能。采用 fastapi+mysql 构建
- mongdb 服务：承担任意的数据结构。可丢弃。采用 moser+ferretdb+postgres 构建
- caddy 服务：服务统一，请求认证。
- tunnel 服务：内网穿透
- 后台数据观察：用 navicat，连接 mongdb 和 mysql 即可。

# api 服务

1. 构建镜像启动容器

```shell
   docker-compose -f api-compose.yml -f mysql-compose.yml up
```

2. 查看 api 文档：

   http://127.0.0.1:80/docs

## 内网测试

```shell
# 如果启动xiaoaitts的话，需要这个配置。小米账号密码。
echo "User=xxx\nPwd=xx" >>.env

docker-compose -f mongo-compose.yml -f mysql-compose.yml -f api-compose.yml -f caddy-compose.yml  -f webdis-compose.yml -f xiaoaitts-compose.yml up -d
```

## 外网测试

```shell
# 如何需要内网穿透的话，需要配置这个。
echo "TUNNEL_TOKEN=eyJhIjxxxxx" >>.env

docker-compose -f tunnel-compose.yml up
```
