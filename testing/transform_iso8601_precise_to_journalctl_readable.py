import os, datetime, sys

TIMESTAMP_READ_FORMAT='%Y-%m-%d %H:%M:%S'

def main():
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <txt file with timestamps>")
    
    with open(sys.argv[1], 'r', encoding='utf-8', newline='') as file:
        tmp = file.readline()
        start = datetime.fromisoformat(tmp[:26] + tmp[29:])
        tmp = file.readline()
        end = datetime.fromisoformat(tmp[:26] + tmp[29:])


    with open(sys.argv[1].split('.') + '_adapted.txt', 'w', encoding='utf-8', newline='\n') as output:
        output.write(f'{start.strftime(TIMESTAMP_READ_FORMAT)}\n')
        output.write(f'{(end + datetime.timedelta(seconds=1)).strftime(TIMESTAMP_READ_FORMAT)}\n')

if __name__ == '__main__':
    main()