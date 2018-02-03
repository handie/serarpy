import serial,time

MSG_SIZE = 4 # bytes 

def get_bit(byteval,idx):
        return ((byteval&(1<<idx))!=0);

ser = serial.serial_for_url('loop://', timeout=1)
ser.write(serial.to_bytes([0x80, 0x81, 0x82, 0xfe, 0x0a, 0x81, 0x82, 0x83, 0x0a]))
cnt = 0
state = []
for i in range(MSG_SIZE*7):
    state.append(0)
while (True):
        x = ''
        if (ser.in_waiting > 0):
                #print(ser.in_waiting)
            x = ser.readline()
            if len(x) - 1 == MSG_SIZE:
                btn = 0
                for i in range(MSG_SIZE):
                    #print(i+1)
                    for j in range(7):
                        is_high = get_bit(x[i],j)
                        if state[btn] != is_high:
                            print('{} value changed to: {}'.format(btn,is_high))
                            state[btn] = is_high 
                        else:
                            print(btn)
                        btn = btn + 1
            elif len(x) > 0:
                    print('wrong number of bytes, input ignored')
        else:
            time.sleep(0.001)
            cnt = cnt + 1
            if cnt == 500:
                ser.write(serial.to_bytes([0x81, 0x81, 0x82, 0xff, 0x0a]))
            if cnt == 1500:
                cnt = 0
                ser.write(serial.to_bytes([0x80, 0x81, 0x82, 0xfe, 0x0a]))
