import time
import datetime
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

FILE_NAME = "custom.log"
CURRENT_APP_RUN:list[str] = []

def get_current_time_string() -> str:
    return datetime.datetime.fromtimestamp(time.time()).strftime(DATE_FORMAT)

def get_timestamp_from_string(date_string) -> float:
    return datetime.datetime.strptime(date_string, DATE_FORMAT).timestamp()

def parse_username_simple(line_to_parse:str):
    #from format USERNAME@IP_ADDR
    at_index = line_to_parse.find("@")
    return line_to_parse[:at_index]

def parse_username(line_to_parse:str):
    #from format "[From:] / [To:] <sip:USERNAME@IP_ADDRESS>..."
    start_index = line_to_parse.find("<sip:")+5 #5 means offset after "<sip:"
    end_index = line_to_parse.find("@")
    return line_to_parse[start_index:end_index]

def file_write_line(line:str):
    with open(FILE_NAME, "a") as file:
        file.write(line + "\n")

def initial_log():
    file_write_line(f"===== Starting server ({get_current_time_string()}) =====")

def log_register(new_user:str):
    line_to_log = f"{get_current_time_string()},REGISTER,{parse_username_simple(new_user)}"
    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_invite(origin, destination):
    line_to_log = f"{get_current_time_string()},INVITE,{parse_username_simple(origin)},{parse_username_simple(destination)}"
    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_ack(data):
    #TODO trosku inac, keby bolo viac roznych konverzacii ?

    last_log = CURRENT_APP_RUN[-1].split(",")[1]

    fromm = parse_username(data[3])
    to = parse_username(data[4])

    line_to_log = None

    if last_log == "INVITE" or last_log == "200":
        line_to_log = f"{get_current_time_string()},CALL STARTED,{fromm},{to}"
    else:
        pass

    if line_to_log != None:
        CURRENT_APP_RUN.append(line_to_log)
        file_write_line(line_to_log)

def log_bye(data):
    now = time.time()
    started_timestamp = get_timestamp_from_string(CURRENT_APP_RUN[-1].split(",")[0])
    call_duration = round(now - started_timestamp, 2)

    fromm = parse_username(data[2])
    to = parse_username(data[3])

    line_to_log = f"{get_current_time_string()},CALL ENDED,{fromm},{to},Call duration: {call_duration} seconds"
    
    CURRENT_APP_RUN.append(line_to_log)
    file_write_line(line_to_log)
    
def log_code(data):
    code = data[0].split(" ")[1]

    fromm = parse_username(data[3])
    to = parse_username(data[4])

    line_to_log = None

    if code == "487":
        line_to_log = f"{get_current_time_string()},487,{fromm},{to},Call hung up by {fromm}"
    elif code == "603":
        line_to_log = f"{get_current_time_string()},603,{fromm},{to},Call hung up by {to}"
    # elif code == "200":
    #     line_to_log = f"200,{fromm},{to},OK DIK"

    if line_to_log != None:
        file_write_line(line_to_log)
        CURRENT_APP_RUN.append(line_to_log)