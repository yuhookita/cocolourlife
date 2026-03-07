require 'webrick'
server = WEBrick::HTTPServer.new(
  Port: 8000,
  DocumentRoot: File.expand_path('..', __dir__)
)
trap('INT') { server.shutdown }
trap('TERM') { server.shutdown }
server.start
