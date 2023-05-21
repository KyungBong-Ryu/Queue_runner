import os
import time
import argparse

def logger(path_file, in_str, write_time=True):
    with open(path_file, "a", encoding='UTF8') as log_txt:
        _str = str(time.strftime('%Y.%m.%d - %H:%M:%S'))
        if write_time:
            log_txt.write(in_str + "       ," + _str + "\n")
        else:
            log_txt.write(in_str + "\n")
    print(in_str)


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'True', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'False', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    
    parser_options = argparse.ArgumentParser(description='_options')
    # set default
    path_q_list                 = "./_Queue_list.txt"                                                   # Queue list. 실행할 command 한 줄에 하나씩 적어두기
    log_q_runner                = "./_Queue_log_" + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + ".txt"    # Queue_runner 실행기록. 파일 없으면 생성후 기록함
    command_restriction         = True                                                                  # command head 제한 여부
    list_allowd_command_head    = ["python", "srun", "#"]                                               # 사용 가능한 command 첫 단어 / #은 comment로 처리 -> 실행 안됨
    list_comment_head           = ["#"]                                                                 # comment 로 인식할 command head list
    
    list_finished = []      # 시도한 command
    list_failed   = []      # 실패한 command 
    
    count_scan_max = 100                 # queue list txt 파일 읽는 횟수
    count_scan     = 0
    
    parser_options.add_argument("--path_in",             type = str,      default = path_q_list,         help = "Path + file name for Queue list text file (str)")
    parser_options.add_argument("--path_out",            type = str,      default = log_q_runner,        help = "Path + file name for Queue log text file (str)")
    parser_options.add_argument("--command_restriction", type = str2bool, default = command_restriction, help = "Command head restriction application (bool)")
    parser_options.add_argument("--scan_max",            type = int,      default = count_scan_max,      help = "Queue list file scan repeat (int)")
    parser_options.add_argument("--wildcard",            type = str,      default = None,                help = "Additional allowed command head (str)")
    
    # argparse -> parser
    args_options        = parser_options.parse_args()
    path_q_list         = args_options.path_in
    log_q_runner        = args_options.path_out
    command_restriction = args_options.command_restriction
    count_scan_max      = args_options.scan_max
    if args_options.wildcard is not None:
        list_allowd_command_head.append(args_options.wildcard)
    
    
    _str = "===============[ Start Queue_runner ]==============="
    logger(log_q_runner, _str)
    
    _str = "Queue list from: " + path_q_list
    logger(log_q_runner, _str, write_time=False)
    
    _str = "Queue list scan repeat: " + str(count_scan_max) + " times"
    logger(log_q_runner, _str, write_time=False)
    
    if command_restriction:
        _str = "Allowed command head: " + ", ".join(list_allowd_command_head)
    else:
        _str = "No restriction applied to command head"
    logger(log_q_runner, _str, write_time=False)
    
    _str = "Comment head: " + ", ".join(list_comment_head)
    logger(log_q_runner, _str, write_time=False)
    
    if args_options.wildcard is None:
        _str = "No wildcard used"
    else:
        _str = "Applied wildcard: " + args_options.wildcard
    logger(log_q_runner, _str, write_time=False)
    
    for count_scan in range(count_scan_max):
        count_scan = count_scan + 1  # (0 ~ n-1) -> (1 ~ n)
        _str = "\n\n\n<>===[ Reading: ( " + path_q_list + " ) " + str(count_scan) + " / " + str(count_scan_max) + " ]===<>"
        logger(log_q_runner, _str)
        try:
            _str = "\n---[ Scanned lists ]---\n"
            logger(log_q_runner, _str, write_time=False)
            with open(path_q_list, "r", encoding='UTF8') as q_list_txt:
                q_list_lines = q_list_txt.readlines()
                _flag_ready = 0
                for q_list_line in q_list_lines:
                    q_command = q_list_line.strip("\n")
                    if q_command.split(" ")[0] in list_allowd_command_head or not command_restriction:
                        if q_command in list_failed:
                            _str = "( Failed  )\t" + q_command
                        elif q_command in list_finished:
                            _str = "( Done    )\t" + q_command
                        elif q_command.split(" ")[0] in list_comment_head:
                            _str = "( Comment )\t" + q_command
                        else:
                            if _flag_ready == 0:
                                _flag_ready = 1
                                _str = "(*Ready  *)\t" + q_command
                            else:
                                _str = "( Pending )\t" + q_command
                    else:
                        _str = "( Denied  )\t" + q_command
                    logger(log_q_runner, _str, write_time=False)
            _str = "\n--- [ Scanned lists ]---\n"
            logger(log_q_runner, _str, write_time=False)
            
            with open(path_q_list, "r", encoding='UTF8') as q_list_txt:
                q_list_lines = q_list_txt.readlines()
                for q_list_line in q_list_lines:
                    q_command = q_list_line.strip("\n")
                    
                    if q_command.split(" ")[0] not in list_allowd_command_head and command_restriction:
                        # not allowd command
                        _str = None
                    elif q_command in list_finished or q_command.split(" ")[0] in list_comment_head:
                        # finished command or comment
                        _str = None
                    else:
                        _str = "===[ Try running... ( " + q_command + " ) ]==="
                        logger(log_q_runner, _str)
                        list_finished.append(q_command)
                        
                        try:
                            _result = os.system(q_command)
                        except:
                            # Case: KeyboardInterrupt
                            _result = None
                        
                        if _result is None:
                            # Case: KeyboardInterrupt
                            list_failed.append(q_command)
                            _str = "===[ FAILURE: Can not run ( " + q_command + " )... maybe KeyboardInterrupt occurred while running ]==="
                        elif _result == 0:
                            # Case: Success
                            _str = "===[ Success: ( " + q_command + " ) ]==="
                        else:
                            # Case: sys.exit() or something
                            list_failed.append(q_command)
                            try:
                                _str = "===[ FAILURE: Error caused ( " + q_command + " ) shut-down with error code ( " + str(_result) + " ) ]==="
                            except:
                                _str = "===[ FAILURE: Error caused ( " + q_command + " ) shut-down with error code ( unknown ) ]==="
                        
                        logger(log_q_runner, _str)
                        break
                if _str is None:
                    _str = "\n===[ no command left to run ]==="
                    logger(log_q_runner, _str, write_time=False)
        except:
            _str = "===[ FAILURE: Can not find ( " + path_q_list + " ) file ]==="
            logger(log_q_runner, _str)
        
        time.sleep(3)
    
    _str = "\n\n\n===============[ Finish Queue_runner ]==============="
    logger(log_q_runner, _str)
    
    
    
    print("EOF: _Queue_runner.py")