from L2.lower.ivirt import IVirt
from L1.lower.results.iresult import IFileLinable

class VirtFileLine(IVirt):
    @classmethod
    def _action_map(cls, self):
        return { IFileLinable: self and self._handle_result }

    def _handle_result(self, pairs, **kwargs):
        pairs += self.prev_output.as_file_line_list()
        self._underlying_prog.run(pairs=pairs, **kwargs)
