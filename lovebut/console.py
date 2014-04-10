from lb.core.admin import AdminCmd
import logging

def _main():
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    cmd = AdminCmd()
    cmd.prompt = "> "
    cmd.cmdloop("Lovebut admin tool. Type ? for help.")

if  __name__ == '__main__':
    _main()