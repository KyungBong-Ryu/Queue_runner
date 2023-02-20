import os
import time

def logger(path_file, in_str):
    with open(path_file, "a") as log_txt:
        _str = str(time.strftime('%Y.%m.%d - %H:%M:%S'))
        log_txt.write(in_str + "       ," + _str + "\n")
    print(in_str)


if __name__ == "__main__":
    _str = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    
    path_q_list = "./_Queue_list.txt"   # Queue list. 실행할 py 파일 이름 + 확장자를 한 줄에 하나씩 적어두기
    log_q_runner = "./_Queue_log_" + _str + ".txt"   # Queue_runner 실행기록. 파일 없으면 생성후 기록함
    
    list_finished = []
    
    count_scan_max = 10                 # queue list txt 파일 읽는 횟수
    count_scan = 0
    
    _str = "===============[ Start Queue_runner ]==============="
    logger(log_q_runner, _str)
    
    for i_scan in range(count_scan_max):
        count_scan = i_scan + 1
        _str = "\n<>===[ Reading: ( " + path_q_list + " ) " + str(count_scan) + " / " + str(count_scan_max) + " ]===<>"
        logger(log_q_runner, _str)
    
        try:
            with open(path_q_list, "r") as q_list_txt:
                q_list_lines = q_list_txt.readlines()
                for q_list_line in q_list_lines:
                    q_name = q_list_line.strip("\n")
                    
                    if q_name in list_finished:
                        _str = "===[ WARNING: ( " + q_name + " ) passed... It has already done ]==="
                        logger(log_q_runner, _str)
                    else:
                        _str = "===[ Try running... ( " + q_name + " ) ]==="
                        logger(log_q_runner, _str)
                        try:
                            is_py = q_name.split(".")[-1]
                            if is_py == "py":
                                _run = "python " + q_name
                                _result = os.system(_run)
                                print("")
                                if _result == 0:
                                    list_finished.append(q_name)
                                    _str = "===[ Success: ( " + q_name + " ) ]==="
                                else:
                                    _str = "***[ FAILURE: Can not run ( " + q_name + " ) ]***"
                            else:
                                _str = "***[ FAILURE: ( " + q_name + " ) is not a .py file ]***"
                            
                            logger(log_q_runner, _str)
                        except:
                            pass
        
        except:
            _str = "***[ FAILURE: Can not find ( " + path_q_list + " ) file ]***"
            logger(log_q_runner, _str)
        
        time.sleep(3)
    
    _str = "\n\n\n===============[ Finish Queue_runner ]==============="
    logger(log_q_runner, _str)
    
    
    
    print("EOF: _Queue_runner.py")
