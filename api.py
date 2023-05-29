import asyncio

# import asynio
import json
from typing import List, Union

import requests


# from symbol import arglist


if __name__ == "__main__":
    api_key = ""
    default_url = ""
else:
    # from ..config import *
    # from ..log import *
    # from ..SqlClass import McsmAccount, McsmDaemon
    # from .string_config import *
    pass

    # from hoshino.modules.myself_bot.SqlClass import
headers = {
    "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
    "Content-Type": "application/json",
}


def get_api_url(
    method,
    url=default_url,
    key=api_key,
    remote_uuid=None,
    instance_uuid=None,
    arg_dict=None,
):
    url = f"{url}{method}?apikey={key}"
    if remote_uuid:
        url += f"&remote_uuid={remote_uuid}"
    if instance_uuid:
        url += f"&uuid={instance_uuid}"
    if arg_dict:
        for key, value in arg_dict.items():
            url += f"&{key}={value}"
    print(url)
    return url


def get_info():
    url = get_api_url("api/overview")
    r = requests.get(url)
    return r.json()


def instance_create(gid, nickname, path, endTime="2093-01-01 00:00:01"):
    """
    _summary_

    Args:
        gid (_type_): _description_
        nickname (_type_): _description_
        path (_type_): _description_
        endTime (_type_): _description_
    """
    # TODO 优先级1 先创建然后再修改信息
    create_instance_data = create_instance_data_config
    # nickname_str  stopCommand_str  path_str  endTime_str image_str ghcr.io/mrs4s/go-cqhttp:master memory_str 500
    instance_data = {
        "nickname_str": nickname,  # "tes2t",
        "path_str": path,  # "/go_cqhttp_data/646464",
        "endTime_str": endTime,  # "2023-01-01 00:00:01",
        "image_str": "ghcr.io/mrs4s/go-cqhttp:1.0.1",
        "memory_str": "300",
    }
    for key, value in instance_data.items():
        create_instance_data = create_instance_data.replace(key, value)
    response = requests.post(
        get_api_url("api/instance", remote_uuid=gid),
        headers=headers,
        data=create_instance_data,
    )
    resp = response.text
    print(resp)
    resp_json = json.loads(resp)
    return resp_json


class McsmInstance:
    def __init__(self, gid, uid):
        self.gid = gid
        self.uid = uid
        self._sh_uid = None

    def __str__(self):
        url = f"http://m#/terminal/{self.gid}/{self.uid}"
        print(str)
        return url

    @property
    def manage_link(self):
        return str(self)

    def edit(self, nickname, path, endTime, gocq_ver="1.0.1"):
        # TODO json打包
        instance_data = {
            "nickname_str": nickname,  # "tes2t",
            "path_str": path,  # "/go_cqhttp_data/646464",
            "endTime_str": endTime,  # "2023-01-01 00:00:01",
            "image_str": f"ghcr.io/mrs4s/go-cqhttp:{gocq_ver}",
            "memory_str": "300",
        }
        create_instance_data = create_instance_data_config
        for key, value in instance_data.items():
            create_instance_data = create_instance_data.replace(key, value)
        response = requests.put(
            get_api_url("api/instance", remote_uuid=self.gid, instance_uuid=self.uid),
            headers=headers,
            data=create_instance_data,
        )
        resp = response.text
        print(resp)
        resp_json = json.loads(resp)
        return resp_json

    @property
    def restart(self):
        return self.control_instance(self, 4)

    def control_instance(
        self, operation_id: Union[int, str], instance_uuid: str = None
    ) -> str:
        """_summary_

        Args:
            operation_id (Union[int,str]): operation_id, open[1] ,stop[2] ,kill[3],restart[4]
            instance_uuid (str, optional): Defaults to McsmInstance's self.uid.

        Returns:
            str: response
        """
        if isinstance(operation_id, int):
            operate_dict = {1: "open", 2: "stop", 3: "kill", 4: "restart"}
            operation_id = operate_dict[operation_id]
        url = get_api_url(
            method=f"api/protected_instance/{operation_id}",
            remote_uuid=self.gid,
            instance_uuid=instance_uuid if instance_uuid else self.uid,
        )
        response = requests.get(url).text
        print(response)
        return response

    def command_input(self, command):
        command = {"command": command}
        url = get_api_url(
            method=f"api/protected_instance/command",
            remote_uuid=self.gid,
            instance_uuid=self.uid,
            arg_dict=command,
        )
        response = requests.post(url).text
        print(response)
        return response

    def get_outputlog(self, raw=False):
        response = requests.get(
            get_api_url(
                "api/protected_instance/outputlog",
                remote_uuid=self.gid,
                instance_uuid=self.uid,
            )
        )
        # import chardet
        # print(chardet.detect(response))
        resp = response.text
        # .encode("utf-8").decode("gbk")
        replace_info = {
            r"\r\n": "\n",
            r"[0m\u001b": "",
            r"\u001b": "",
            ") 内 ": ") 内 \n",
            "[37m": "",
            "[33m": "",
            "[48;5;": "",
            "0m": "",
            "7m": "",
            "[\n": "",
            " ": "",
            "(qrcode.png)": f"(qrcode.png)\n{'-'*99}\n二维码可能因为本地没有登录成功,如果已经确认登录成功请联系管理员\n{'-'*99}",
        }
        for key, value in replace_info.items():
            resp = resp.replace(key, value)

        # print(resp)
        if not raw:
            resp = resp.split("\n")[-20:-1]
            for i, line in enumerate(resp):
                if len(line) > 60:
                    resp[i] = line[:60] + "..."
            resp = "\n".join(resp)
        # print(resp)  # TODO: 2022年11月8日  修复输出日志问题测试点
        # print(resp.decode("utf-8").encode("gbk"))
        # try:
        #     print(resp)
        # except Exception as e:
        #     print(str(e))
        return resp

    def edit_file(self, file_path, file_content=None):
        file_data = {
            "target": file_path,  # "/go_cqhttp_data/646464/config.json",
            # "text": file_content,
        }
        if file_content:
            file_data["text"] = file_content
        response = requests.put(
            get_api_url("api/files", remote_uuid=self.gid, instance_uuid=self.uid),
            data=file_data,
        )
        resp = response.text
        print(resp)
        return resp

    def get_file(self, file_path):
        file_data = {
            "target": file_path,  # "/go_cqhttp_data/646464/config.json",
            # "text": file_content,
        }

        response = requests.put(
            get_api_url("api/files", remote_uuid=self.gid, instance_uuid=self.uid),
            data=file_data,
        )
        resp = response.text
        print(resp)
        resp = json.loads(resp)
        return resp["data"]

    def mkdir(self, path):
        path_data = {"target": path}
        response = requests.post(
            get_api_url(
                "api/files/mkdir", remote_uuid=self.gid, instance_uuid=self.uid
            ),
            data=path_data,
        )
        print(response.text)
        return response.text

    async def bot_docker_init(self):
        """_summary_
        time spend : 25s
        """
        try:
            # TODO 启动sh实例
            self.control_instance(1, self.sh_uid)
            await asyncio.sleep(3)
            self.control_instance(1)
            await asyncio.sleep(3)
            self.command_input("233")
            await asyncio.sleep(5)
            self.control_instance(3)
            await asyncio.sleep(5)
            self.control_instance(1)
            await asyncio.sleep(12)
            self.control_instance(3)
            await asyncio.sleep(5)
            # self.control_instance(1)
            # await asyncio.sleep(10)
            # self.control_instance(3)
        except Exception as e:
            print(e)
            return f"出现错误:{e}"
        return "创建成功"

    # @run_sync
    def upload_file(self, file, file_name: str = None, remote_dir: str = ""):
        file_name = file_name if file_name else file
        remote_dir = f"""%2F{remote_dir}"""
        url = get_api_url(
            "api/files/upload",
            remote_uuid=self.gid,
            instance_uuid=self.uid,
            arg_dict={"upload_dir": remote_dir},
        )
        response = requests.get(url)
        upload_info = json.loads(response.text)
        ws_url = upload_info["data"]["addr"]
        ws_passwd = upload_info["data"]["password"]
        # TODO put to upload file
        upload_url = f"http://{ws_url}/upload/{ws_passwd}"
        # Content-Type: multipart/form-data

        file_data = {
            "file": (
                file_name,
                open(file, "rb"),
                "multipart/form-data",
                {"Expires": "0"},
            )
        }
        response = requests.post(upload_url, files=file_data)
        print(response.text)
        return response.text

    def download_file(self):
        pass

    def delete_self(self):
        # headers = {"Content-Type": "application/json"}
        url = get_api_url("api/instance", remote_uuid=self.gid)
        data = {"uuids": [self.uid], "deleteFile": False}
        # 只能str转 不能用json 否则就是奇奇怪怪的bug 返回200实际失败
        # payload = "{\"uuids\": [\"del_uuid\"], \"deleteFile\": false}"
        # data = payload.replace("del_uuid", self.uid)
        # response = requests.delete(url, data=data)
        print(data)
        response = requests.delete(url, json=data)
        print(response.text)
        return response.text

    # {"targets":[["/device.json","/device.json2"]]}
    # http://mcsm.isam.top/api/files/move?remote_uuid=5c777273c66244b9b2ed1870947886d9&uuid=f0118b24183544149e19afa1e16257fa&token=085639b05e8f4d5384a197e5026bf4f81678525935385
    def move_file(self, file_path, target_path):
        # Content-Type: application/json; charset=utf-8
        # {"targets":[["/device.json","/device.json2"]]}
        headers = {"Content-Type": "application/json"}
        url = get_api_url(
            "api/files/move", remote_uuid=self.gid, instance_uuid=self.uid
        )
        data = {"targets": [[file_path, target_path]]}
        print(data)
        response = requests.put(url, json=data)
        return response.text

    # TODO 完整性检查，检查session.token和device.json文件是否存在
    def check_instance(self):
        pass

    def get_file_list(self, target: str = "/", page: int = 0) -> dict:
        """_summary_

        Args:
            target (str, optional): _description_. Defaults to "/".
            page (int, optional): _description_. Defaults to 0.

        Returns:
            dict: _description_
            其中["files"]为文件列表,["folders"]为文件夹列表
        """
        url = get_api_url(
            "api/files/list",
            remote_uuid=self.gid,
            instance_uuid=self.uid,
            arg_dict={
                "target": f"{target}",
                "page": page,
                "page_size": 40,
            },
        )
        response = requests.get(url)
        json_data = json.loads(response.text)
        statu_code = json_data["status"]
        assert statu_code == 200, f"请求失败:{json_data}"
        # json_data = json_data["data"]["items"]
        json_data["files"] = []
        json_data["folders"] = []
        for file in json_data["data"]["items"]:
            if file["type"] == 1:
                json_data["files"].append(file["name"])
            else:
                json_data["folders"].append(file["name"])
        return json_data


class McsmUser:
    def __init__(self, user_qq=0, pw=0):
        self.user_qq = user_qq
        self.ac = user_qq
        self.pw = pw

    # 创建用户
    def user_create(self):
        url = get_api_url("api/auth")
        data = {
            "username": f"{self.user_qq}",
            "password": f"{self.pw}",
            "permission": 1,
        }
        response = requests.post(url, data=data)
        resp = response.text
        print(resp)
        # TODO save uuid to mysql
        uuid = self.get_name_last_register_uuid(self.user_qq)
        McsmAccount.create(
            account=self.user_qq, password=self.pw, uuid=uuid, owner=self.user_qq
        )
        return resp

    # 获得全部该名字用户
    def search_user_info(self, name=None):
        name = self.user_qq if name is None else name
        url = get_api_url(
            "api/auth/search", arg_dict={"userName": name, "page": 1, "page_size": 99}
        )
        response = requests.get(url)
        resp = response.text
        print(resp)
        return json.loads(resp)

    # 获得搜索到的用户里最后注册的uuid
    def get_name_last_register_uuid(self, name=None):
        # TODO 判断相同名字来获得uuid

        name = self.user_qq if name is None else name
        user_info = self.search_user_info(name)
        return user_info["data"]["data"][-1]["uuid"]

# TODO ...有空改
# nickname_str  stopCommand_str  path_str  endTime_str image_str ghcr.io/mrs4s/go-cqhttp:master memory_str 500
# TODO: 什么傻逼玩意
create_instance_data_config = """{
  "nickname": "nickname_str",
  "startCommand": "start",
  "stopCommand": "^c",
  "cwd": "path_str",
  "ie": "UTF-8",
  "oe": "UTF-8",
  "createDatetime": null,
  "lastDatetime": null,
  "type": "universal",
  "tag": [],
  "endTime": "endTime_str",
  "fileCode": "UTF-8",
  "processType": "docker",
  "terminalOption": {
    "haveColor": true
  },
  "eventTask": {
    "autoStart": false,
    "autoRestart": false,
    "ignore": false
  },
  "docker": {
    "image": "image_str",
    "ports": null,
    "memory": "memory_str",
    "networkMode": "bridge",
    "cpusetCpus": null,
    "cpuUsage": "3",
    "maxSpace": null,
    "io": null,
    "network": null
  },
  "pingConfig": {
    "ip": "",
    "port": 25565,
    "type": 1
  }
}
    """
# nickname_str  stopCommand_str  path_str  endTime_str image_str ghcr.io/mrs4s/go-cqhttp:master memory_str 500
