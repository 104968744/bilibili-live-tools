from bilibili import bilibili
from statistics import Statistics
from printer import Printer
import rafflehandler
from configloader import ConfigLoader
import utils
import asyncio
import websockets
import struct
import json
import re
import sys


async def DanMuraffle(area_id, connect_roomid, messages):
    try:
        dic = json.loads(messages)
    except:
        return
    cmd = dic['cmd']
    '''
    if cmd == 'DANMU_MSG':
        # print(dic)
        Printer().printlist_append(['danmu', '弹幕', 'user', dic])
        return
    '''    
    if cmd == 'PREPARING':
        Printer().printlist_append(['join_lottery', '', 'user', f'{area_id}分区检测器下播！将切换监听房间'], True)  
        return False  
    if cmd == 'SYS_GIFT':
        if 'giftId' in dic.keys():
            if str(dic['giftId']) in bilibili.get_giftids_raffle_keys():
                
                text1 = dic['real_roomid']
                text2 = dic['url']
                giftId = dic['giftId']
                Printer().printlist_append(['join_lottery', '', 'user', "检测到房间{:^9}的{}活动抽奖".format(text1, bilibili.get_giftids_raffle(str(giftId)))], True)
                rafflehandler.Rafflehandler.Put2Queue((giftId, text1, text2), rafflehandler.handle_1_room_activity)
                Statistics.append2pushed_raffle('活动', area_id=area_id)
                        
            elif dic['giftId'] == 39:
                Printer().printlist_append(['join_lottery', '', 'user', "节奏风暴"])
                temp = await bilibili.get_giftlist_of_storm(dic)
                check = len(temp['data'])
                if check != 0 and temp['data']['hasJoin'] != 1:
                    id = temp['data']['id']
                    json_response1 = await bilibili.get_gift_of_storm(id)
                    print(json_response1)
                else:
                    Printer().printlist_append(['join_lottery','','debug', [dic, "请联系开发者"]])
            else:
                text1 = dic['real_roomid']
                text2 = dic['url']
                Printer().printlist_append(['join_lottery', '', 'debug', [dic, "请联系开发者"]])
                try:
                    giftId = dic['giftId']
                    Printer().printlist_append(['join_lottery', '', 'user', "检测到房间{:^9}的{}活动抽奖".format(text1, bilibili.get_giftids_raffle(str(giftId)))], True)
                    rafflehandler.Rafflehandler.Put2Queue((giftId, text1, text2), rafflehandler.handle_1_room_activity)
                    Statistics.append2pushed_raffle('活动', area_id=area_id)
                            
                except:
                    pass
                
        else:
            Printer().printlist_append(['join_lottery', '普通送礼提示', 'user', ['普通送礼提示', dic['msg_text']]])
        return
    if cmd == 'SYS_MSG':
        if dic.get('real_roomid', None) is None:
            Printer().printlist_append(['join_lottery', '系统公告', 'user', dic['msg']])
        else:
            try:
                TV_url = dic['url']
                real_roomid = dic['real_roomid']
                # print(dic)
                type_text = (dic['msg'].split(':?')[-1]).split('，')[0].replace('一个', '')
                Printer().printlist_append(['join_lottery', '小电视', 'user', f'{area_id}分区检测器检测到房间{real_roomid:^9}的{type_text}抽奖'], True)
                # url = "https://api.live.bilibili.com/AppSmallTV/index?access_key=&actionKey=appkey&appkey=1d8b6e7d45233436&build=5230003&device=android&mobi_app=android&platform=android&roomid=939654&ts=1521734039&sign=4f85e1d3ce0e1a3acd46fcf9ca3cbeed"
                rafflehandler.Rafflehandler.Put2Queue((real_roomid,), rafflehandler.handle_1_room_TV)
                Statistics.append2pushed_raffle(type_text, area_id=area_id)
                
            except:
                print('请联系开发者', dic)
    if cmd == 'GUARD_MSG':
        print(dic)
        a = re.compile(r"(?<=在主播 )\S+(?= 的直播间开通了总督)")
        res = re.search(a, dic['msg'])
        if res is not None:
            print(str(res.group()))
            name = str(res.group())
            Printer().printlist_append(['join_lottery', '', 'user', f'{area_id}分区检测器检测到房间{name:^9}开通总督'], True)
            rafflehandler.Rafflehandler.Put2Queue((((name,), utils.find_live_user_roomid),), rafflehandler.handle_1_room_captain)
            Statistics.append2pushed_raffle('总督', area_id=area_id)
        
  
def printDanMu(area_id, messages):

    try:
        dic = json.loads(messages)
    except:
        print(messages)
        return
    cmd = dic['cmd']
    # print(cmd)
    if cmd == 'DANMU_MSG':
        # print(dic)
        Printer().printlist_append(['danmu', '弹幕', 'user', dic])
        return          
                                                          

class bilibiliClient():
    
    __slots__ = ('ws', 'connected', '_UserCount', 'roomid', 'raffle_handle', 'area_id')

    def __init__(self, roomid=None, area_id=None):
        self.ws = None
        self.connected = False
        self._UserCount = 0
        if roomid is None:
            self.roomid = ConfigLoader().dic_user['other_control']['default_monitor_roomid']
            self.area_id = 0
            self.raffle_handle = False
        else:
            self.roomid = roomid
            self.area_id = area_id
            self.raffle_handle = True

    # 待确认    
    async def close_connection(self):
        try: 
            await self.ws.close()
        except :
            print('请联系开发者', sys.exc_info()[0], sys.exc_info()[1])
        self.connected = False
        
    async def CheckArea(self):
        while self.connected:
            # await asyncio.sleep(300)
            area_id = await utils.FetchRoomArea(self.roomid)
            if area_id != self.area_id:
                print(f'主播更换分区{self.area_id}为{area_id}，即将切换至新的有效分区(请反馈)')
                break
            await asyncio.sleep(300)
        
    async def connectServer(self):
        try:
            self.ws = await websockets.connect('ws://broadcastlv.chat.bilibili.com:2244/sub')
        except:
            print("# 连接无法建立，请检查本地网络状况")
            print(sys.exc_info()[0], sys.exc_info()[1])
            return False
        if (await self.SendJoinChannel(self.roomid)):
            self.connected = True
            Printer().printlist_append(['join_lottery', '', 'user', f'连接弹幕服务器{self.roomid}成功'], True)
            # await self.ReceiveMessageLoop()
            return True

    async def HeartbeatLoop(self):
        Printer().printlist_append(['join_lottery', '', 'user', '弹幕模块开始心跳（由于弹幕心跳间隔为30s，所以后续正常心跳不再提示）'], True)

        while self.connected:
            await self.SendSocketData(0, 16, ConfigLoader().dic_bilibili['_protocolversion'], 2, 1, "")
            await asyncio.sleep(30)

    async def SendJoinChannel(self, channelId):
        body = f'{{"uid":0,"roomid":{channelId},"protover":1,"platform":"web","clientver":"1.3.3"}}'
        await self.SendSocketData(0, 16, ConfigLoader().dic_bilibili['_protocolversion'], 7, 1, body)
        return True

    async def SendSocketData(self, packetlength, magic, ver, action, param, body):
        bytearr = body.encode('utf-8')
        if not packetlength:
            packetlength = len(bytearr) + 16
        sendbytes = struct.pack('!IHHII', packetlength, magic, ver, action, param)
        if len(bytearr) != 0:
            sendbytes = sendbytes + bytearr
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), sendbytes)
        try:
            await self.ws.send(sendbytes)
        except websockets.exceptions.ConnectionClosed:
              print("# 主动关闭或者远端主动关闭.")
              await self.ws.close()
              self.connected = False
              return None
        except:
            print(sys.exc_info()[0], sys.exc_info()[1])
            self.connected = False

    async def ReadSocketData(self):
        bytes_data = b''
        try:
            bytes_data = await asyncio.wait_for(self.ws.recv(), timeout=35.0)
            # print('hhhhh')
        except asyncio.TimeoutError:
              print('# 由于心跳包30s一次，但是发现35内没有收到任何包，说明已经悄悄失联了，主动断开')
              await self.ws.close()  
              self.connected = False
              return None
        except websockets.exceptions.ConnectionClosed:
              print("# 主动关闭或者远端主动关闭")
              await self.ws.close()
              await self.ws.close()  
              self.connected = False
              return None
        except:
            #websockets.exceptions.ConnectionClosed'>
            print(sys.exc_info()[0], sys.exc_info()[1])
            print('请联系开发者')
            await self.ws.close()
            self.connected = False
            return None
        # print(tmp) 
           
        # print('测试0', bytes_data)                    
        return bytes_data
    
                    
    async def ReceiveMessageLoop(self):
        if self.raffle_handle:
            while self.connected:
                bytes_datas = await self.ReadSocketData()
                if bytes_datas is None:
                    break
                len_read = 0
                while len_read < len(bytes_datas):
                    state = None
                    split_header = struct.unpack('!I2H2I', bytes_datas[len_read:16+len_read])
                    len_data, len_header, ver, opt, seq = split_header
                    remain_data = bytes_datas[len_read+16:len_read+len_data]
        
                    if len_data != 16:
                        if opt == 3:
                            num3, = struct.unpack('!I', remain_data)
                            self._UserCount = num3
                        elif opt == 5:
                            try:
                                messages = remain_data.decode('utf-8')
                            except:
                                self.connected = False
                                print(bytes_datas[len_read:len_read + len_data])
                            state = await DanMuraffle(self.area_id, self.roomid, messages)
                        elif opt == 8:
                            pass
                        else:
                            self.connected = False
                            print(bytes_datas[len_read:len_read + len_data])
                                
                    if state is not None and not state:
                        return       
                    len_read += len_data
        else:
            while self.connected:
                bytes_datas = await self.ReadSocketData()
                if bytes_datas is None:
                    break
                len_read = 0
                # print(bytes_datas)
                while len_read < len(bytes_datas):
                    state = None
                    split_header = struct.unpack('!I2H2I', bytes_datas[len_read:16 + len_read])
                    len_data, len_header, ver, opt, seq = split_header
                    remain_data = bytes_datas[len_read + 16:len_read + len_data]
                    
                    # print(split_header)
                    if len_data != 16:
                        if opt == 3:
                            num3, = struct.unpack('!I', remain_data)
                            self._UserCount = num3
                        elif opt == 5:
                            try:
                                messages = remain_data.decode('utf-8')
                            except:
                                self.connected = False
                                print('风风光光刚回家', bytes_datas[len_read:len_read + len_data])
                            state = printDanMu(self.area_id, messages)
                        elif opt == 8:
                            pass
                        else:
                            self.connected = False
                            print(bytes_datas[len_read:len_read + len_data])
                                
                    if state is not None and not state:
                        return       
                    len_read += len_data 
                    
               
    
