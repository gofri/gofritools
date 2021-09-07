from L5 import BatchMode

class PipeMode(BatchMode):
    def __init__(self, *args, **kwargs):
        BatchMode.__init__(self, *args, force_pipe=True, **kwargs)
