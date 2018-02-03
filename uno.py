import serial,time,requests

HUE_BRIDGE = 'http://192.168.1.160'
HUE_USER = 'KqUnd-9hMBmyLMorJeBUY38tis0gimRrf5ipi9vx'

MSG_SIZE = 4 # bytes 

def get_bit(byteval,idx):
        return ((byteval&(1<<idx))!=0);

ser = serial.Serial('/dev/cu.usbmodem1411', 9600, timeout=1)
time.sleep(1)
print(ser.name)
print(ser.is_open)
cnt = 0
state = []

headers = {'charset': 'utf-8'}
url = ''.join([HUE_BRIDGE , '/api/' , HUE_USER , '/lights' , '/1' , '/state'])

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
                            if is_high == True:
                                data = {'on': True}
                            else:
                                data = {'on': False}
                            response = requests.put(url, json=data, headers=headers)
                            print(url)
                            print(response.status_code)
                            print(response.json())
                            state[btn] = is_high 
                        btn = btn + 1
            elif len(x) > 0:
                    print('wrong number of bytes, input ignored')
        else:
            time.sleep(0.05)
