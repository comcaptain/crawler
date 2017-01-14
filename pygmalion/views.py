from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pygmalion.common.file_scanner import FileScanner, DirectoryInformationEncoder


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'pygmalion'}


@view_defaults(renderer="string")
class CrawlingResultViewer:

    def __init__(self, request):
        self.request = request

    @view_config(route_name="novels")
    def novels(self):
        return FileScanner("d:/temp/").scan()

# below code is for debug
if __name__ == '__main__':
    config = Configurator()
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('novels', '/novels')
    config.scan()
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()