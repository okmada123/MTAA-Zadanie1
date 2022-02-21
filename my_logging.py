FILE_NAME = "custom.log"
CURRENT_APP_RUN:list[str] = []

def file_write_line(line:str):
    with open(FILE_NAME, "a") as file:
        file.write(line + "\n")

def initial_log():
    file_write_line(f"===== Starting server (CAS XY) =====")

def log_register(new_user):
    line_to_log = f"REGISTER,{new_user}"
    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_invite(origin, destination):
    line_to_log = f"INVITE,{origin},{destination}"
    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_ack(data):
    #TODO trosku inac, keby bolo viac roznych konverzacii

    last_log = CURRENT_APP_RUN[-1].split(",")[0]

    #print(data)
    fromm = data[4]
    to = data[5]

    line_to_log = None

    if last_log == "INVITE" or last_log == "200":
        line_to_log = f"CALL STARTED,{fromm},{to},CAS"
    else:
        pass

    if line_to_log != None:
        CURRENT_APP_RUN.append(line_to_log)
        file_write_line(line_to_log)

def log_bye(data):
    time_started = CURRENT_APP_RUN[-1].split(",")[-1]
    line_to_log = f"CALL ENDED,FROM,TO,{time_started}" #TODO - from, to dorobit a cas tiez, ze kolko trval
    
    CURRENT_APP_RUN.append(line_to_log)
    file_write_line(line_to_log)
    

def log_code(data):
    code = data[0].split(" ")[1]
    #print(code)
    fromm = data[3]
    to = data[4]
    #print(code, data[3], data[4])

    line_to_log = None

    if code == "100":
        #print(f"Trying to reach [{to}] from [{fromm}]")
        pass
    # elif code == "180":
    #     print(f"Ringing on [{to}] from [{fromm}]")
    elif code == "487":
        line_to_log = f"487,{fromm},{to},Call hung up by [{fromm}]"
    elif code == "603":
        line_to_log = f"603,{fromm},{to},Call hung up by [{to}]"
    # elif code == "200":
    #     line_to_log = f"200,{fromm},{to},OK DIK"

    if line_to_log != None:
        file_write_line(line_to_log)
        CURRENT_APP_RUN.append(line_to_log)