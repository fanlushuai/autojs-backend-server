from fastapi import Depends, FastAPI, Request, Response
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import base62
from . import crud, models, schemas
from .database import SessionLocal, engine
import time, math
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

print(os.getcwd())
models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_schedule_or_create_blank():
    global Schedule
    try:
        Schedule = AsyncIOScheduler()
        # 每10s，踢掉，不健康设备
        Schedule.start()
        Schedule.add_job(dropUnhealthDevice, trigger="interval", seconds=15)
        # 每天，加载一次所有的有效设备
        Schedule.add_job(loadAlldeviceId, trigger="interval", days=1)
        logger.info("创建定时任务")
    except:
        logger.error("创建定时任务 异常")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_schedule_or_create_blank()
    loadAlldeviceId()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# Dependency
def get_db(request: Request):
    return request.state.db


@app.post("/key/gen/{unit}", response_model=schemas.Rsp)
def gen_key(count: int, unit: str, db: Session = Depends(get_db)):
    """生成有效卡密"""

    if "day" == unit:
        endtimeSec = count * 60 * 60 * 24 + int(time.time())
    elif "week" == unit:
        endtimeSec = count * 60 * 60 * 24 * 7 + int(time.time())
    elif "month" == unit:
        endtimeSec = count * 60 * 60 * 24 * 31 + int(time.time())

    elif "year" == unit:
        endtimeSec = count * 60 * 60 * 24 * 366 + int(time.time())
    else:
        return "errot param path"

    # key = crud.create_key(db, str(uuid.uuid1()), endtimeSec)
    key = crud.create_key(db, base62.genCode(), endtimeSec)
    return {"data": key.key}


@app.post("/key/device", response_model=schemas.Rsp)
def bind_key_device(info: schemas.Info, db: Session = Depends(get_db)):
    """绑定，key和设备"""
    # 验证卡密
    key = crud.get_key(db, info.key)
    if key == None:
        return {"msg": "key not valid", "status": "001"}

    # 验证 & 添加设备
    device = crud.get_device(db, info.deviceId)
    if device == None:
        crud.create_device(db, info.key, info.deviceId)
        loadAlldeviceId()
    return {"data": "ok"}


@app.get("/device/group")
def all_group():
    """查看所有分组"""
    return {"data": sorted(devices_active.items())}


@app.post("/device/keepAlive")
def keepAlive(requestRole: schemas.requestRole, response_model=schemas.Rsp):
    """客户端 保活

    return 分组
    """
    deviceId = requestRole.deviceId
    role = requestRole.role

    validPass = False
    global deviceList
    for devices in deviceList:
        if str(devices.device_id) == deviceId:
            validPass = True
            break

    if not validPass:
        return {"status": "not valid"}

    currentTimeSec = int(time.time())
    doReGroup = False
    if devices_active.get(deviceId) == None:
        devices_active.setdefault(deviceId, {})["active_Time"] = currentTimeSec
        devices_active.setdefault(deviceId, {})["role"] = role
        devices_active.setdefault(deviceId, {})["group"] = "no finder"

        doReGroup = True
    else:
        devices_active[deviceId]["active_Time"] = currentTimeSec
        if devices_active[deviceId]["role"] != role:
            devices_active[deviceId]["role"] = role
            doReGroup = True
    if doReGroup:
        reGroup()

    return {"data": devices_active[deviceId]["group"]}


devices_active = {
    # "example-device-Id": {"active_Time": 1701970220, "role": "getter", "group": "#1"}
}

group_max_num = 10


deviceList = []


def loadAlldeviceId():
    """加载所有有效设备，到内存"""

    session = SessionLocal()
    global deviceList
    try:
        logger.info("加载有效设备数据到内存")
        deviceList = crud.list_valid_device(session)
    finally:
        session.close()


def dropUnhealthDevice():
    """踢掉未按时保活的设备"""

    logger.info("检查设备")
    currentTimeSec = int(time.time())
    timeout = 15  # 15s没有响应的。直接认为设备掉线。直接踢掉。重新分配成员。

    dropCount = 0
    doReGroup = False
    for key in list(devices_active.keys()):
        if currentTimeSec - timeout > devices_active[key]["active_Time"]:
            # 踢掉设备，重新分组
            if devices_active[key]["role"] == "finder":
                doReGroup = True
            devices_active.pop(key)
            dropCount += 1
            logger.info("踢掉设备：%s", key)

    if doReGroup:
        reGroup()

    return dropCount > 0


def reGroup():
    """节点自动重新分组"""

    logger.info("重新分组")
    # 发现者总数量
    finder_count = 0
    for key in list(devices_active.keys()):
        if devices_active[key]["role"] == "finder":
            finder_count += 1
    if finder_count < 1:
        logger.info("没有发现者")
        for key in list(devices_active.keys()):
            devices_active[key]["group"] = "_noFinder"
            # devices_active[key][
            #     "group"
            # ] = "_0"  # 如果大家还想要消费，单机模式的。其实单机模式就是finder。所以，不存在nofinder。
            # 内部客户端，遇到nofinder，直接走_0通道。
            # 外部客户端，遇到nofinder，就gg
        return devices_active

    devices_count = len(devices_active)
    if devices_count <= group_max_num:
        logger.info("设备总数量太少，全部分为1组")
        group_num = "_1"
        for key in list(devices_active.keys()):
            devices_active[key]["group"] = group_num
        return devices_active

    # 组数量
    group_count = math.ceil(devices_count / group_max_num)  # 向上取整

    # 组编码
    group_num = []
    for num in range(1, group_count + 1):
        group_num.append("_" + str(num))

    # 每一组发现者数量
    group_finder_min_count = int(finder_count / group_count)  # 向下取整,那么会导致多出来几个，发现者

    if group_finder_min_count > 0:
        left_finder_count = finder_count - group_finder_min_count * group_count

        group_finder_count = []
        # 讲多出来的，进行平均分配
        for num in range(1, group_count + 1):
            if left_finder_count > 0:
                left_finder_count -= 1
                group_finder_count.append(group_finder_min_count + 1)
            else:
                group_finder_count.append(group_finder_min_count)

        group_num_getter_index = 0
        current_getter_count = 0

        group_num_finder_index = 0
        current_finder_count = 0

        for key in list(devices_active.keys()):
            if devices_active[key]["role"] == "getter":
                devices_active[key]["group"] = group_num[group_num_getter_index]
                current_getter_count += 1

                group_getter_count = (
                    group_max_num - group_finder_count[group_num_getter_index]
                )
                if current_getter_count == group_getter_count:
                    group_num_getter_index += 1
                    current_getter_count = 0
            if devices_active[key]["role"] == "finder":
                devices_active[key]["group"] = group_num[group_num_finder_index]
                current_finder_count += 1
                if current_finder_count == group_finder_count[group_num_finder_index]:
                    group_num_finder_index += 1
                    current_finder_count = 0
    else:  # 发现者少，组太多。
        # 按照，发现者的数量进行平均分配。
        new_group_max_num = math.ceil(devices_count / finder_count)  # 向上取整
        group_finder_count = 1
        # 组数量
        group_num = finder_count

        # 组编码
        group_num = []
        for num in range(1, group_count + 1):
            group_num.append("_" + str(num))

        group_num_getter_index = 0
        current_getter_count = 0

        group_num_finder_index = 0

        for key in list(devices_active.keys()):
            if devices_active[key]["role"] == "getter":
                devices_active[key]["group"] = group_num[group_num_getter_index]
                current_getter_count += 1

                group_getter_count = new_group_max_num - group_finder_count
                if current_getter_count == group_getter_count:
                    group_num_getter_index += 1
                    current_getter_count = 0
            if devices_active[key]["role"] == "finder":
                devices_active[key]["group"] = group_num[group_num_finder_index]
                group_num_finder_index += 1
    return devices_active
