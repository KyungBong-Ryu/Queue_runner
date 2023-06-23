import os
import sys
import time
import argparse
import subprocess

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
    _str_time =  str(time.strftime('%Y_%m_%d_%H_%M_%S'))                                                # 현재 시간 기록
    
    parser_options = argparse.ArgumentParser(description='_options')
    # set default
    path_q_list                 = "./_Queue_list.txt"                                                   # Queue list. 실행할 command 한 줄에 하나씩 적어두기
    # path_q_out                  = "./" + path_q_list.split("/")[-1].split(".")[0] + "_log_" + _str_time # Queue_runner 실행기록 저장폴더
    
    command_restriction         = True                                                                  # command head 제한 여부
    list_allowd_command_head    = ["python", "srun", "#"]                                               # 사용 가능한 command 첫 단어 / #은 comment로 처리 -> 실행 안됨
    list_comment_head           = ["#"]                                                                 # comment 로 인식할 command head list
    
    
    # ignore_fail -> hook_result -> hook_runout, hook_runerr
    hook_runout                 = False                                                                 # command 실행 결과 output hook 여부
    hook_runerr                 = False                                                                 # command 실행 결과 error  hook 여부
    hook_count                  = 0
    
    list_finished = []      # 시도한 command
    list_failed   = []      # 실패한 command 
    dict_hooked   = {}      # hook 된 command
    
    count_scan_max = 100                 # queue list txt 파일 읽는 횟수
    count_scan     = 0
    
    parser_options.add_argument("--path_in",             type = str,      default = path_q_list,         help = "Path + file name for Queue list text file (str)")
    parser_options.add_argument("--path_out",            type = str,      default = None,                help = "Path + file name for Queue log text file (str)")
    parser_options.add_argument("--command_restriction", type = str2bool, default = command_restriction, help = "Command head restriction application (bool)")
    parser_options.add_argument("--scan_max",            type = int,      default = count_scan_max,      help = "Queue list file scan repeat (int)")
    parser_options.add_argument("--wildcard",            type = str,      default = None,                help = "Additional allowed command head (str)")
    parser_options.add_argument("--hook_runout",         type = str2bool, default = hook_runout,         help = "Hook command output (bool)")
    parser_options.add_argument("--hook_runerr",         type = str2bool, default = hook_runerr,         help = "Hook command error (bool)")
    
    # argparse -> parser 
    args_options    = parser_options.parse_args()
    path_q_list     = args_options.path_in
    
    if args_options.path_out is None:
        path_q_out = "./" + path_q_list.split("/")[-1].split(".")[0] + "_log_" + _str_time  # Queue_runner 실행기록 저장폴더
    else:
        path_q_out = args_options.path_out
        
        if path_q_out[-1] == "/":
            path_q_out = path_q_out[:-1]
        
        path_q_out = path_q_out + _str_time
    
    if not os.path.exists(path_q_out):
        os.makedirs(path_q_out)
    
    log_q_runner = path_q_out + "/log_Queue_runner.txt"  # Queue_runner 실행로그. 파일 없으면 생성후 기록함.
    
    command_restriction = args_options.command_restriction
    count_scan_max      = args_options.scan_max
    if args_options.wildcard is not None:
        list_allowd_command_head.append(args_options.wildcard)
    hook_runout         = args_options.hook_runout
    hook_runerr         = args_options.hook_runerr
    
    _str = "===============[ Start Queue_runner ]==============="
    logger(log_q_runner, _str)
    
    _str = "Queue_runner log to: " + path_q_out
    logger(log_q_runner, _str, write_time=False)
    
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
    
    _str = "Hook run output: " + str(hook_runout) + ", error: " + str(hook_runerr)
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
                            try:
                                _hook_num = dict_hooked[q_command]
                                _id = "Fail " + str(_hook_num) + "      "
                                _str = "( " + _id[:7] + " )\t" + q_command
                            except:
                                _str = "( Failed  )\t" + q_command
                        elif q_command in list_finished:
                            try:
                                _hook_num = dict_hooked[q_command]
                                _id = "Done " + str(_hook_num) + "      "
                                _str = "( " + _id[:7] + " )\t" + q_command
                            except:
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
                        
                        _result = None                  # Case: KeyboardInterrupt
                        
                        if hook_runout or hook_runerr:
                            hook_count += 1
                            dict_hooked[q_command] = hook_count
                            path_log_hook = path_q_out + "/log_hook_" + str(hook_count) + ".txt"
                            
                            with open(path_log_hook, "w", encoding='UTF8') as log_hook:
                                _str = "Run command was...\n\t" + q_command + "\n\n"
                                log_hook.write(_str)
                            
                            with open(path_log_hook, "a", encoding='UTF8') as log_hook:
                                # command 실행 결과 hook 시행
                                try:
                                    # check=True를 통해 q_command 실행 실패시 오류 발생시킴
                                    # https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
                                    if hook_runout and hook_runerr:
                                        _run_result = subprocess.run([q_command]
                                                                    ,stdout=log_hook, stderr=log_hook
                                                                    ,shell=True, check=True
                                                                    ,encoding='utf-8',errors='utf-8', text=True
                                                                    )
                                    elif hook_runout:
                                        _run_result = subprocess.run([q_command]
                                                                    ,stdout=log_hook, stderr=sys.stderr
                                                                    ,shell=True, check=True
                                                                    ,encoding='utf-8',errors='utf-8', text=True
                                                                    )
                                    elif hook_runerr:
                                        _run_result = subprocess.run([q_command]
                                                                    ,stdout=sys.stdout, stderr=log_hook
                                                                    ,shell=True, check=True
                                                                    ,encoding='utf-8',errors='utf-8', text=True
                                                                    )
                                    _result =_run_result.returncode
                                except:
                                    _result = -9
                        else:
                            # command 실행 결과 hook 시행 안함 (v 1.5.x 방법)
                            _result = os.system(q_command)
                        
                        if _result is None:
                            # Case: KeyboardInterrupt
                            list_failed.append(q_command)
                            _str = "===[ FAILURE: Can not run ( " + q_command + " )... maybe KeyboardInterrupt occurred while running ]==="
                        elif _result == 0:
                            # Case: Success
                            _str = "===[ Success: ( " + q_command + " ) ]==="
                        elif _result == -9:
                            # case: FAIL with subprocess.run
                            _str = "===[ FAILURE: ( " + q_command + " ) with subprocess.run ]==="
                            list_failed.append(q_command)
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