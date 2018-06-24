import asyncio
import utils
from bilibiliCilent import bilibiliClient
from printer import Printer
from bilibili import bilibili
from configloader import ConfigLoader
import random

     
async def check_room_state(roomid):
    json_rsp = await bilibili.req_room_init(roomid)
    state = json_rsp['data']['live_status']
    return state

async def get_one(areaid):
    # 1 娱乐分区
    # 2 游戏分区
    # 3 手游分区
    # 4 绘画分区
    if areaid == 1:
        roomid = 23058
        # print(roomid)
        state = await check_room_state(roomid)
        if state == 1:
            print(areaid, roomid)
            return roomid
            
    while True:
        json_rsp = await bilibili.req_realroomid(areaid)
        data = json_rsp['data']
        roomid = random.choice(data)['roomid']
        # print(roomid)
        state = await check_room_state(roomid)
        if state == 1:
            # print('ok')
            break
        else:
            print("检测到房间未开播，立即尝试重新获取")
    print(areaid, roomid)
    return roomid


class connect():
    __slots__ = ('danmuji')
    instance = None
    
    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(connect, cls).__new__(cls, *args, **kw)
            cls.instance.danmuji = None
        return cls.instance
        
    async def run(self):
        while True:
            print('# 正在启动弹幕姬')
            time_start = int(utils.CurrentTime())
            self.danmuji = bilibiliClient()
            task_connect = asyncio.ensure_future(self.danmuji.connectServer())
            connect_results = await asyncio.gather(task_connect)
            # print(connect_results)
            if all(connect_results):
                pass
            else:
                continue
            task_main = asyncio.ensure_future(self.danmuji.ReceiveMessageLoop())
            task_heartbeat = asyncio.ensure_future(self.danmuji.HeartbeatLoop())
            finished, pending = await asyncio.wait([task_main, task_heartbeat], return_when=asyncio.FIRST_COMPLETED)
            print('# 弹幕姬异常或主动断开，处理完剩余信息后重连')
            self.danmuji.connected = False
            time_end = int(utils.CurrentTime())
            if not task_heartbeat.done():
                task_heartbeat.cancel()
                await self.danmuji.close_connection()
                print('# 弹幕主程序退出，立即取消心跳模块')
            else:
                await asyncio.wait(pending)
                print('# 弹幕心跳模块退出，主程序剩余任务处理完毕')
            if time_end - time_start < 5:
                print('# 当前网络不稳定，为避免频繁不必要尝试，将自动在5秒后重试')
                await asyncio.sleep(5)
    
    @staticmethod
    async def reconnect(roomid):
        ConfigLoader().dic_user['other_control']['default_monitor_roomid'] = roomid
        print('已经切换roomid')
        if connect.instance.danmuji is not None:
            await connect.instance.danmuji.close_connection()
        
        
class RaffleConnect():
    def __init__(self, areaid):
        self.danmuji = None
        self.roomid = None
        self.areaid = areaid
        
    async def run(self):
        while True:
            self.roomid = await get_one(self.areaid)
            print('# 正在启动弹幕姬')
            time_start = int(utils.CurrentTime())
            self.danmuji = bilibiliClient(self.roomid, self.areaid)
            task_connect = asyncio.ensure_future(self.danmuji.connectServer())
            connect_results = await asyncio.gather(task_connect)
            # print(connect_results)
            if all(connect_results):
                pass
            else:
                continue
            task_main = asyncio.ensure_future(self.danmuji.ReceiveMessageLoop())
            task_heartbeat = asyncio.ensure_future(self.danmuji.HeartbeatLoop())
            task_checkarea = asyncio.ensure_future(self.danmuji.CheckArea())
            finished, pending = await asyncio.wait([task_main, task_heartbeat, task_checkarea], return_when=asyncio.FIRST_COMPLETED)
            print('# 弹幕姬异常或主动断开，处理完剩余信息后重连')
            self.danmuji.connected = False
            time_end = int(utils.CurrentTime())
            if not task_heartbeat.done():
                task_heartbeat.cancel()
                await self.danmuji.close_connection()
                print('# 弹幕主程序退出，立即取消心跳模块')
            else:
                await asyncio.wait(pending)
                print('# 弹幕心跳模块退出，主程序剩余任务处理完毕')
            if time_end - time_start < 5:
                print('# 当前网络不稳定，为避免频繁不必要尝试，将自动在5秒后重试')
                await asyncio.sleep(5)
            
            

        
                    
