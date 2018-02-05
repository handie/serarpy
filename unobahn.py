import serial,time,requests
import asyncio
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.asyncio.websocket import WebSocketServerFactory

HUE_BRIDGE = 'http://192.168.1.160'
HUE_USER = 'KqUnd-9hMBmyLMorJeBUY38tis0gimRrf5ipi9vx'

MSG_SIZE = 4 # bytes 

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {} bytes".format(len(payload)))
        else:
            print("Text message received: {}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

def get_bit(byteval,idx):
        return ((byteval&(1<<idx))!=0);

factory = WebSocketServerFactory()
factory.protocol = MyServerProtocol

loop = asyncio.get_event_loop()
coro = loop.create_server(factory, '127.0.0.1', 9000)
server = loop.run_until_complete(coro)

try:
   loop.run_forever()
except KeyboardInterrupt:
   pass
finally:
   server.close()
   loop.close()

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(1)
print(ser.name)
print(ser.is_open)
cnt = 0
state = []

headers = {'charset': 'utf-8'}
url_light = ''.join([HUE_BRIDGE , '/api/' , HUE_USER , '/lights' , '/1' ])
url_state = ''.join([url_light , '/state' ])

for i in range(MSG_SIZE*7):
    state.append(0)
while (True):
        x = ''
        if (ser.in_waiting > 0):
            x = ser.readline()
            if len(x) - 1 == MSG_SIZE:
                btn = 0
                for i in range(MSG_SIZE):
                    for j in range(7):
                        is_high = get_bit(x[i],j)
                        if state[btn] != is_high:
                            print('{} value changed to: {}'.format(btn,is_high))
                            response = requests.get(url_light) 
                            print(response.json())
                            json = response.json()
                            if is_high == True:
                                if json['state']['on'] == False:
                                    data = {'on': True}
                                else:
                                    data = {'on': False}
                            response = requests.put(url_state, json=data, headers=headers)
                            print(url_state)
                            print(response.status_code)
                            print(response.json())
                            state[btn] = is_high 
                        btn = btn + 1
            elif len(x) > 0:
                    print('wrong number of bytes, input ignored')
        else:
            time.sleep(0.05)
