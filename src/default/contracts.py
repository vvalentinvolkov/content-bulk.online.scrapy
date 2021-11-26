import json

from scrapy.contracts import Contract


class RequestCbKwargsContract(Contract):
    """ Контракт: проверяет cb_kwargs из возвращаемых Request
        @request_cb_kwargs {"arg1": "value1", "arg2": "value2", ...}
    """

    name = 'request_cb_kwargs'

    def post_process(self, output):
        for request in output:
            request.cb_kwargs = json.loads(' '.join(self.args))
            return args