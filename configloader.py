import configparser
import webcolors
import codecs

# "#969696"
def hex_to_rgb_percent(hex_str):
    color = webcolors.hex_to_rgb_percent(hex_str)
    
    return [float(i.strip('%'))/100.0 for i in color]


# "255 255 255"
def rgb_to_percent(rgb_str):
    color = webcolors.rgb_to_rgb_percent(map(int, rgb_str.split()))
    
    return [float(i.strip('%'))/100.0 for i in color]

    

    
        
def load_bilibili(file):
    cf_bilibili = configparser.ConfigParser()
    cf_bilibili.optionxform = str
    
    cf_bilibili.read_file(codecs.open(file, "r", "utf8"))
    dic_bilibili = cf_bilibili._sections
    
                
    dic_nomalised_bilibili = dic_bilibili['normal'].copy()
    
    dic_nomalised_bilibili['account'] = dic_bilibili['account'].copy()
    if dic_nomalised_bilibili['account']['username']:
        pass
    else:
        username = input("# 输入帐号: ")
        password = input("# 输入密码: ")
        cf_bilibili.set('account', 'username', username)
        cf_bilibili.set('account', 'password', password)
        cf_bilibili.write(codecs.open(file, "w+", "utf8"))
        dic_nomalised_bilibili['account']['username'] = username
        dic_nomalised_bilibili['account']['password'] = password
        
    
        
    dic_bilibili_type = dic_bilibili['types']
    # str to int
    for i in dic_bilibili_type['int'].split():
        
        dic_nomalised_bilibili[i] = int(dic_bilibili['normal'][i])
            
    # str to bool
    # for i in dic_bilibili_type['bool'].split():
    
        # dic_nomalised_bilibili[i] = True if dic_bilibili['normal'][i] == 'True' else False

               
        
        # str to dic
    for i in dic_bilibili.keys():
        # print(i)
        if i[0:3] == 'dic':
            dic_nomalised_bilibili[i[4:]] = dic_bilibili[i]
            
    
                
    
    return dic_nomalised_bilibili
        
def load_color(file):
    cf_color = configparser.ConfigParser()
    
    cf_color.read_file(codecs.open(file, "r", "utf8"))

    dic_color = cf_color._sections
    for i in dic_color.values():
        for j in i.keys():
            if i[j][0] == '#':
                i[j] = hex_to_rgb_percent(i[j])
            else:
                i[j] = rgb_to_percent(i[j])
                    
    return dic_color
        
def load_user(file):
    cf_user = configparser.ConfigParser()
    cf_user.read_file(codecs.open(file, "r", "utf8"))
    dic_user = cf_user._sections
    dictionary ={
            'True':True, 
            'False': False,
            'user': 0,
            'debug': 1
        }
            
    for i in dic_user['print_control'].keys():
        dic_user['print_control'][i] = dictionary[dic_user['print_control'][i]]
            
    return dic_user
    
    
class ConfigLoader():
    
    instance = None

    def __new__(cls, colorfile = None, userfile = None, bilibilifile = None):
        if not cls.instance:
            cls.instance = super(ConfigLoader, cls).__new__(cls)
            cls.instance.dic_color = load_color(colorfile)
            # print(self.dic_color)
        
            cls.instance.dic_user = load_user(userfile)
            #print(self.dic_user)
        
            cls.instance.dic_bilibili = load_bilibili(bilibilifile)
            # print(self.dic_bilibili)
            print("# 初始化完成")
        return cls.instance
        
            
       
        


