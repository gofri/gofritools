from L5.iopmode import IOpMode
from common import logging, ui_tools, utils
import sys

class BatchMode(IOpMode):
    def __init__(self, stack, parser, args):
        self.stack = stack
        self.args = args

    def run(self):
        cmd_res = self.stack.put(self.args)
        if utils.is_pipe(sys.stdout):
            # XXX: need to write this way because is binary data
            sys.stdout.buffer.write(self.stack.picklize())
        else:
            # print (default to human-readable)
            self.args.output_type = self.args.output_type or utils.OutputTypes.human 
            cmd_res = cmd_res.stringify_by_args(**vars(self.args))
            print(cmd_res)
