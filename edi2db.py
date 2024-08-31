import sqlite3
import os
import glob
import chardet

conn = sqlite3.connect('logfiles.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS edi_logs (
    date TEXT,
    time TEXT,
    send_call TEXT,
    send_locator,
    call TEXT,
    mode TEXT,
    send_rst TEXT,
    rcvd_rst TEXT,
    rcvd_locator TEXT,
    qrb TEXT
)
''')
conn.commit()

def read_file_with_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        return raw_data.decode(encoding)

logfile_dir = 'logfiles'
edi_files = glob.glob(os.path.join(logfile_dir, '*.edi'))

for edi_file in edi_files:
    content = read_file_with_encoding(edi_file)
    lines = content.splitlines()

    for line in lines:
        if 'PCall=' in line:		
            send_call = line.split('=',1)[1]
        if 'TDate=' in line:
            date = line.split('=',1)[1]
            day1 = date.split(';',1)[0]
            day2 = date.split(';',1)[1]
            l = list(day1)
            del(l[0:2])
            record_day1=''.join(l)
            l = list(day2)
            del(l[0:2])
            record_day2=''.join(l)
        if 'PWWLo=' in line:
            send_locator = line.split('=',1)[1]

    for line in lines:    
        if ((record_day1 in line) or (record_day2 in line)) and ('TDate=' not in line):
            parts = line.split(";", -1)

            date = parts[0] 
            time = parts[1]  
            call = parts[2]
            mode = parts[3]

            # mixed modes are allways TX/RX
            match mode:
                case "0": 
                    mode = "none"
                case "1":
                    mode = "SSB"
                case "2":
                    mode = "CW"
                case "3":
                    mode = "SSB/CW"
                case "4":
                    mode = "CW/SSB"
                case "5":
                    mode = "AM"
                case "6":
                    mode = "FM"
                case "7":
                    mode = "RTTY"
                case "8":
                    mode = "SSTV"
                case "9":
                    mode = "ATV"

            send_rst = parts[4]
            rcvd_rst = parts[6]
            rcvd_locator = parts[9]
            qrb = parts[10]

            cursor.execute('''
            INSERT INTO edi_logs (date, time, send_call, send_locator, call, mode, send_rst, rcvd_rst, rcvd_locator, qrb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, time, send_call, send_locator, call, mode, send_rst, rcvd_rst, rcvd_locator, qrb))
            conn.commit()

conn.close()