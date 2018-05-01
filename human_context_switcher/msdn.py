import urllib
import bs4
from google import google

class MSDN(object):
    def __init__(self, function_name):
        self.function_name = function_name
        self._parse()

    def _get_url(self):
        results = list(google.search(self.function_name))
        if len(results) == 0:
            print('Failed to find function {}'.format(self.function_name))
            return None
        pattern = '{} function'.format(self.function_name)
        self.msdn_url = next(x.link for x in results if pattern in x.name and x.name.endswith('MSDN - Microsoft'))
        return self.msdn_url

    def _parse(self):
        if self._get_url() is None:
            return
        data = urllib.request.urlopen(self.msdn_url).read()
        soup = bs4.BeautifulSoup(data, 'html.parser')
        text = soup.getText()
        syntax_block = text.split('Syntax\n')[1]
        syntax_block, parameters_block = syntax_block.split('Parameters\n')[0:2]
        parameters_block, return_value_block = parameters_block.split('Return value\n')[0:2]
        return_value_block, other = return_value_block.split('Remarks\n')[0:2]

        syntax_block = syntax_block.split('\n')
        function_index = [index for index,x in enumerate(syntax_block) if self.function_name in x][0]
        syntax_block = '\n'.join(syntax_block[function_index:])
        self.syntax = syntax_block.strip()
        self.parameters = parameters_block.strip()
        self.return_value = return_value_block.strip()
        self.other = other.strip()
