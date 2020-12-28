import traceback

import lib.service as service

if __name__ == '__main__':
    print("Start service")
    try:
        service.run()
    except:
        print(traceback.format_exc())
        exit(0)
