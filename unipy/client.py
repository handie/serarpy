from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import requests
import threading

class MyClientProtocol(WebSocketClientProtocol):

    appConfig = {}
    units = {}

    @classmethod
    def setAppConfig(cls,config):
        cls.appConfig = config
        for unit in cls.appConfig['units']:
            cls.units[unit['name']] = unit

    def __init__(self):
        self.clicks = {}
        self.holds = {}

    def onConnect(self, response):
        # print("Connected: {0}".format(response))

        for unit in self.appConfig['units']:
            ws_peer = "tcp:{}:{}".format(unit['host'],unit['port'])
            if ws_peer == response.peer:
                self.unit = unit
                break

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        
        if not isBinary:            
        
            obj = json.loads(format(payload.decode('utf8')))
          
            if obj['dev'] in self.unit['dev']:
          
                if obj['dev'] == 'input':
          
                    digital_input_config = self.unit['dev']['input']
                    
                    if obj['circuit'] in digital_input_config['circuit']:
                    
                        circuit_config = digital_input_config['circuit'][obj['circuit']]
                        
                        x = "{}.{}.{}".format(self.unit['name'],'input',obj['circuit'])             

                        if 'onTrue' in circuit_config and obj['value'] == 1:                            
                            self.performActions(circuit_config,'onTrue')
                        
                        if 'onFalse' in circuit_config and obj['value'] == 0:                            
                            self.performActions(circuit_config,'onFalse')
                        
                        if ( 'onClick' in circuit_config or 'onLongClick' in circuit_config ):
                        
                            if obj['value'] == 1:                                                        
                                self.clicks[x] = obj['time']
                        
                            elif obj['value'] == 0 and x in self.clicks:                                                        
                                diff =  ( obj['time'] - self.clicks[x] ) / 1000
                                self.clicks.pop(x)
                                if diff < 300:
                                    if 'onClick' in circuit_config:
                                        self.performActions(circuit_config,'onClick')
                                else:
                                    if 'onLongClick' in circuit_config:
                                        self.performActions(circuit_config,'onLongClick')
                        
                        if 'onHold' in circuit_config and obj['value'] == 1:                            
                            print('hold')
                            if x in self.holds:
                                self.holds[x].cancel
                                self.holds.pop(x)
                                print(x+" timer thread cancelled")
                            else:
                                h = self.unit['host']
                                u = "http://{}/rest/{}/{}".format(h,obj['dev'],obj['circuit'])                            
                                t = threading.Timer(0.4, self.held, [x,u])
                                self.holds[x] = t
                                t.start() 

    def held(self,id,url):
        g = requests.get(url)
        circuit = g.json()
        if circuit['value'] == 1 and id in self.holds:
            print(id+' held')
            t = threading.Timer(0.1, self.held, [id,url])
            t.start() 
        else:
            print(id+' released')
            if id in self.holds:
                self.holds.pop(id)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def performActions(self,circuit_config,event):
        print('executing {} actions'.format(event))
        for action in circuit_config[event]['actions']:
            #print('{} {} {}'.format(action['unit'],action['action'],action['circuit']))
            h = self.units[action['unit']]['host']
            
            if action['action'] == 'switch':                                        
            
                p = requests.post("http://{}/rest/{}/{}".format(h,action['dev'],action['circuit']), data={'value': action['value']})            
            
            elif action['action'] == 'toggle':
            
                g = requests.get("http://{}/rest/{}/{}".format(h,action['dev'],action['circuit']))
                circuit = g.json()
                if circuit['value'] == 0:
                    new_val = 1
                else:
                    new_val = 0
                p = requests.post("http://{}/rest/{}/{}".format(h,action['dev'],action['circuit']), data={'value': new_val})            


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    with open('config.json', 'r') as f:    
        config = json.load(f)

    MyClientProtocol.setAppConfig(config)

    loop = asyncio.get_event_loop()

    factory = WebSocketClientFactory(u"ws://192.168.1.100/ws")
    factory.protocol = MyClientProtocol
    conn = loop.create_connection(factory, '192.168.1.100', 80)
    loop.run_until_complete(conn)
    
    # factory = WebSocketClientFactory(u"ws://127.0.0.1:9020")
    # factory.protocol = MyClientProtocol    
    # conn = loop.create_connection(factory, 'localhost', 9020)
    # loop.run_until_complete(conn)

    loop.run_forever()
    loop.close()
