import sys
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
        raise SystemExit(f"Usage: {sys.argv[0]} <node_number> <filtered input from squeue/sed>")
        
    try:
        # assumption: if there is a suspended job, there will be 2 arguments due to query format
        arg2 = sys.argv[2]
        arg3 = sys.argv[3]
    except IndexError:
        sb.run(["bash", "systemctl", "enable", "--now", "wasimoff_provider.service"])
        return
    
    node_number = int(arg1)
    translation_table = dict.fromkeys(map(ord, 'com[]'), None)
    alloc_nodes = arg3.translate(translation_table)
    if not check_if_node_in_alloc(node_number, alloc_nodes):
        sb.run(["bash", "systemctl", "enable", "--now", "wasimoff_provider.service"])
        


if __name__ == '__main__':
    main()
