import sys, os, serial, time, string

'''
try:
    from serial.tools.list_ports import comports
except ImportError:
    comports = None
'''

DEFAULT_PORT = None
DEFAULT_BAUDRATE = 115200
DEFAULT_RTS = False
DEFAULT_DTR = False
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE
DEFAULT_RDTIMEOUT = None
DEFAULT_FLOWCONTROL = False
DEFAULT_WRTIMEOUT = None
DEFAULT_INTERCHARTIMEOUT = None

comPortStr = "COM"
openPort = False
command1 = "debug command dsp_device log on"
# command2 = "debug command dsp_device emi 136000000 869975000 60000 100 25000"
command2 = "debug command dsp_device emi 136000000 174000000 60000 100 25000"
command3 = "debug command dsp_device log print"
userCommand = ''
output = ''
fileName = ''
fileNameGraph = ''

ser = serial.Serial(
    port = DEFAULT_PORT,
    baudrate = DEFAULT_BAUDRATE,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

while openPort == False:
    #Get COM Port from user
    comPortNum = raw_input("Type in COM port number: \r\n")
    
    DEFAULT_PORT = comPortStr + comPortNum
    
    #Configure serial port
    '''
    ser = serial.Serial(
        port = DEFAULT_PORT,
        baudrate = DEFAULT_BAUDRATE,
        parity = DEFAULT_PARITY,
        stopbits = DEFAULT_STOPBITS,
        bytesize = DEFAULT_BYTESIZE
    )
    '''
    ser.port = DEFAULT_PORT
    try:
        ser.open()

    except Exception, e:
        print "error opening serial port: " + str(e) + "\r\n"
        openPort = False

    if ser.isOpen():
        openPort = True
        print "serial open"
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput() #flush output buffer, aborting current output

    else:
        print " Cannot open serial port \r\n" + DEFAULT_PORT

loop = True

while loop :
    userCommand = raw_input("Type start to get radio ready \r\n You will have 30 seconds to get to EMC Chamber \r\n")
    if userCommand == 'start':
        # send the first command 
        ser.write('\r' + command1 + '\r')
        # wait one second to give radio time to respond
        time.sleep(1)
        while ser.inWaiting() > 0 :
            output += ser.read(1)
        if output != '':
            print output

        # wait two second before sending next command
        time.sleep(2)
        output = ''

        ser.write('\r')
        # wait one second to give radio time to respond
        time.sleep(1)
        while ser.inWaiting() > 0 :
            output += ser.read(1)
        if output != '':
            print output

        # wait one second before sending next command
        time.sleep(1)
        output = ''

        # send the second command
        ser.write(command2)
        time.sleep(1)
        ser.write('\r')
        # wait one second to give radio time to respond
        time.sleep(1)
        while ser.inWaiting() > 0 :
            output += ser.read(1)
        if output != '':
            print output
            loop = False
            print "You have 30 seconds to get to the EMC Chamber"
            time.sleep(30)
    
    else:
        print "Wrong command"
        loop = True

# Wait 15 mins
print "Wait 15 mins, then go get radio"
timeStart = time.time()
minutes = 6
loop = True
while loop:
    time.sleep(1)
    timeRemaining = int(time.time() - timeStart) - minutes * 60
    if timeRemaining == 0:
        loop = False

    else:
        loop = True

print "Go get Radio"

userCommand = raw_input("Is Radio connected? Yes or No \r\n")
while userCommand != 'Yes':
    if userCommand == 'No':
        userCommand = raw_input("Is Radio connected now? Yes or No \r\n")

fileName = raw_input("A log will now be created \r\n Please enter a file name now: \r\n")
fileNameGraph = fileName + 'Graph' + '.csv'
fileName += '.csv'

#Create file
file = open(fileName, "w")

ser.flushInput() #flush input buffer, discarding all its contents
ser.flushOutput() #flush output buffer, aborting current output

output = ''
ser.write('\r' + command3 + '\r')
# wait one second for radio to respond
time.sleep(1)
while ser.inWaiting() > 0:
    output += ser.read(1)
    if output != '':
        print output
        file.write(output)
        output = ''

# Close file
file.close()
ser.close()

print "File will now be parsed for errors result given\r\n"

y=[]
i=0;
strHolder = ''
last=0.0
db=0.0
with open(fileName) as f, open(fileNameGraph, 'w') as graph:
    for line in f:
        i+=1
        print str(i)
        # print repr(line)
        #freq= float(line[:8])
        #db = float(line[10:])

        if line in ['\n', '\r\n'] or len(line) < 26 or len(line) > 35:
            print "Nothing on line"
            time.sleep(1)
            continue
            
        if not contains_digits(line):
            print "No number on line"
            time.sleep(1)
            continue
        else:
            if str.isdigit(line.split(' ')[2]):
                freq = float(line.split(' ')[2])
            else:
                print "No freq here"
                continue
            
            strHolder = line.split(' ')[4]
            holder = strHolder.rstrip('\r\n')
            
            if holder.isdigit():
                db = float(line.split(' ')[4])
                graph.write(line.rstrip('\r'))
            else:
                print "No float here"
                continue
                time.sleep(10)

            freq = freq/1000.0
            db = db * (-10.0)/100.0
            y.append(db)

            '''
            if (freq-last==25.0) or (freq-last==50.0): continue
            else: print 'sample '+str(i)+' incorrect freq interval '+str(freq-last)
            '''
            #print str(i)+' '+str(freq)+' '+str(db)
            last=freq
            if i > 8441:break
            
# close file
graph.close()

exceedcount=0
count=0
levelcount=0
for i in y:
    count+=1
    if i > -120.0:
        exceedcount += 1
        print str(count)
    if i > -100.0:
        levelcount += 1

print 'db items:'+str(i)
print 'level count 100dB:'+str(levelcount)

if ((float(exceedcount)/count) > 0.020):
    print 'FAILED -> '+str(exceedcount)+' out of '+str(len(y))
else:
    print 'PASS -> '+str(exceedcount)+' out of '+str(len(y))

userCommand = raw_input("Enter any character to quit")

