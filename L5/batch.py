from L5.lower.iopmode import IOpMode
from common import logging, ui_tools, utils
import sys

class BatchMode(IOpMode):
    def __init__(self, stack, parser, args, force_pipe=False):
        self.stack = stack
        self.args = args
        self.force_pipe = force_pipe

    def run(self):
        logging.set_verbosity(self.args.verbosity)
        logging.verbose_print(self.args, min_verbosity=logging.VERBOSE_3)
        cmd_res = self.stack.put(self.args)
        if utils.is_pipe(sys.stdout) or self.force_pipe:
            # XXX: need to write this way because is binary data
            sys.stdout.buffer.write(self.stack.picklize())
        else:
            # print (default to human-readable)
            self.args.output_type = self.args.output_type or utils.OutputTypes.human 
            cmd_res = cmd_res.stringify_by_args(**vars(self.args))
            print(cmd_res)
