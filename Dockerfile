FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./api /code/api

ENV CONNECTION="mysql+mysqlconnector://fls:fls@127.0.0.1:3306/test"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]

# https://blog.51cto.com/u_16175473/7690694  传环境变量，注意参数的位置。
# docker run -e CONNECTION="mysql+mysqlconnector://fls:fls@0.0.0.0:3306/test" --name fastapi -p 80:80 fastapi