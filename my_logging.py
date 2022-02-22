import time
import datetime
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

FILE_NAME = "custom.log"
CURRENT_APP_RUN:list[str] = []

#constants which get logged in the .log file
REGISTER = "REGISTER"
INVITE = "INVITE"
CALL_STARTED = "CALL STARTED"
CALL_ENDED = "CALL ENDED"
SWITCH_INVITE = "SWITCH INVITE"
SWITCH_ACK = "SWITCH ACK"
CODE_487 = "487"
CODE_603 = "603"

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

def find_last_log(username1:str, username2:str) -> str | None:
    # Finds last communication in logs, between username1 and username2
    index = len(CURRENT_APP_RUN)-1
    while index >= 0:
        split_line = CURRENT_APP_RUN[index].split(",")
        index -= 1

        if split_line[1] == REGISTER:
            continue
        else:
            fromm = split_line[2]
            to = split_line[3]
            if (username1 == fromm or username1 == to) and (username2 == fromm or username2 == to):
                return ",".join(split_line)
    return None

def find_call_start_log(username1:str, username2:str) -> str:
    index = len(CURRENT_APP_RUN)-1
    while index >= 0:
        split_line = CURRENT_APP_RUN[index].split(",")
        index -= 1

        if split_line[1] != CALL_STARTED:
            continue
        else:
            fromm = split_line[2]
            to = split_line[3]
            if (username1 == fromm or username1 == to) and (username2 == fromm or username2 == to):
                return ",".join(split_line)

def file_write_line(line:str):
    with open(FILE_NAME, "a") as file:
        file.write(line + "\n")

def initial_log():
    file_write_line(f"===== Starting server ({get_current_time_string()}) =====")

def log_register(new_user:str):
    line_to_log = f"{get_current_time_string()},{REGISTER},{parse_username_simple(new_user)}"
    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_invite(origin, destination):
    fromm = parse_username_simple(origin)
    to = parse_username_simple(destination)
    last_log = find_last_log(fromm, to)

    if last_log == None:
        #log new call
        line_to_log = f"{get_current_time_string()},{INVITE},{fromm},{to}"
    else:
        status = last_log.split(",")[1]
        if status == CALL_ENDED or status == CODE_603 or status == CODE_487:
            line_to_log = f"{get_current_time_string()},{INVITE},{fromm},{to}"
        else:
            #otherwise it is a request for switch from voice to video and vice versa
            line_to_log = f"{get_current_time_string()},{SWITCH_INVITE},{fromm},{to}"

    file_write_line(line_to_log)
    CURRENT_APP_RUN.append(line_to_log)

def log_ack(data):
    fromm = parse_username(data[3])
    to = parse_username(data[4])

    last_log = find_last_log(fromm, to)
    if last_log == None:
        return
    last_log = last_log.split(",")[1]

    line_to_log = None

    if last_log == INVITE:
        line_to_log = f"{get_current_time_string()},{CALL_STARTED},{fromm},{to}"
    elif last_log == SWITCH_INVITE:
        line_to_log = f"{get_current_time_string()},{SWITCH_ACK},{fromm},{to}"
    else:
        return

    if line_to_log != None:
        CURRENT_APP_RUN.append(line_to_log)
        file_write_line(line_to_log)

def log_bye(data):
    now = time.time()

    fromm = parse_username(data[2])
    to = parse_username(data[3])

    started_timestamp = get_timestamp_from_string(find_call_start_log(fromm, to).split(",")[0])
    call_duration = round(now - started_timestamp, 2)


    line_to_log = f"{get_current_time_string()},{CALL_ENDED},{fromm},{to},Call duration: {call_duration} seconds"
    
    CURRENT_APP_RUN.append(line_to_log)
    file_write_line(line_to_log)
    
def log_code(data):
    code = data[0].split(" ")[1]

    fromm = parse_username(data[3])
    to = parse_username(data[4])

    line_to_log = None

    if code == "487": #these are code numbers sent in SIP headers, cannot be changed
        line_to_log = f"{get_current_time_string()},{CODE_487},{fromm},{to},Call hung up by {fromm}"
    elif code == "603":
        line_to_log = f"{get_current_time_string()},{CODE_603},{fromm},{to},Call hung up by {to}"

    if line_to_log != None:
        file_write_line(line_to_log)
        CURRENT_APP_RUN.append(line_to_log)