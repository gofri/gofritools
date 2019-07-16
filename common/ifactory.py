from abc import abstractmethod


class IFactory(object):

    @abstractmethod
    def create(self, *args, **kwargs):
        pass
