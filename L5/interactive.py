from common import logging, ui_tools, utils
from L4.stack import Stack
from L5.lower.iopmode import IOpMode
from L5 import argparse as gofriparse

class InteractiveMode(IOpMode):
    def __init__(self, stack, parser, args):
        self.stack = stack
        self.args = args
        self.parser = parser
        self.verbosity = args.verbosity # base verbosity for all cmds

    @property
    def __verbosity(self):
        def args_ver():
            try:    return self.args.verbosity
            except: return 0

        return self.verbosity + args_ver()

    def run(self):
        info = False
        cmd_res = None

        gofriparse.init_parsing_completion(interactive=True)
        try:
            # Welcoming gesture if entering interactive mode without command
            if not self.args.command:
                print('Hey, welcome to gofritools interactive mode!')
                self.parser = gofriparse.make_parser(interactive=True, virt=False) # adjust parser for help
                self.parser.print_help()
                self.args = None

            while True:
                # Handle next cmd
                try:
                    if self.args:
                        logging.set_verbosity(self.__verbosity)
                        if self.args.command:
                            logging.verbose_print(f'Handling next command: {self.args.command}')
                            if self.args.command == 'quit':
                                print('Goodbye!')
                                break
                            cmd_res = self.stack.put(self.args)
                            info = False
                except Stack.OpMessage as e:
                    logging.print_warning(e)
                    info = True
                    failed = False # stack ops failure
                except (Exception, SystemExit) as e:
                    info = True
                    logging.print_warning(e)
                    if logging.global_verbosity > 1:
                        logging.log_ex()  # TODO this is ugly

                if cmd_res:
                    if not (self.__verbosity or info):
                        ui_tools.clear_screen()
                        print(f'Result:\n===\n{cmd_res.humanize()}\n===\n')

                # Read next cmd
                parser = gofriparse.make_parser(interactive=True, virt=True)

                try:
                    cmdline = gofriparse.read_cmdline(">>> ")
                    self.args = gofriparse.parse_args(parser, cmdline)
                except EOFError:
                    raise
                except (Exception, SystemExit) as e:
                    # Remove current command and retry naturally
                    info = True
                    self.args = None

        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            print('Exiting due to user interrupt (ctrl-C)')
            return 0
        except EOFError:
            ### handle keyboard exit ###
            print('Exiting due to user exit (ctrl-D)')
            return 0
