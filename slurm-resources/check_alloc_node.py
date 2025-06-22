import sys, functools
import subprocess as sb

def check_if_node_in_alloc(node_number, alloc_nodes):
    for expr in alloc_nodes.split(','):
       try:
           node_number_tmp = int(expr)
           if node_number == node_number_tmp:
               return True
       except ValueError:
           tmp = expr.split('-')
           start = int(tmp[0])
           end = int(tmp[1])
           if node_number in range(start,end+1):
               return True
    return False

def main():
    try:
        arg1 = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <node_number> <filtered input from squeue/sed as pairs>")
    
    len_sys_argv = len(list(sys.argv))
        
    if len_sys_argv % 2 == 1:
        raise SystemExit("missing inputs from hostname or sed")
    elif len_sys_argv < 3:
        sb.run(["sudo", "systemctl", "enable", "--now", "wasimoff_provider.service"])
        return
    
    node_number = int(arg1)
    translation_table = dict.fromkeys(map(ord, 'com[]'), None)
    cond = functools.reduce(lambda acc, y: acc and not check_if_node_in_alloc(node_number, sys.argv[y].translate(translation_table)), list(range(3,len_sys_argv,2)), True)
    if cond:
        sb.run(["sudo", "systemctl", "enable", "--now", "wasimoff_provider.service"])


if __name__ == '__main__':
    main()
