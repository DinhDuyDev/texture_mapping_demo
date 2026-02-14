class DelLink:
    def __init__(self, obj, source:list|set):
        self.obj = obj
        self.source = source
    def delete_link(self):
        self.source.remove(self.obj)

class Deleter:
    delete_queue:list[DelLink] = []
    @classmethod
    def delete_all_requests(cls):
        for request in Deleter.delete_queue:
            request.delete_link()
        Deleter.delete_queue.clear()
        # print(f"Deleter queue:{Deleter.delete_queue}")
    @classmethod
    def request_delete(cls, obj, container_to_delete_from:list|set):
        Deleter.delete_queue.append(DelLink(obj, container_to_delete_from))