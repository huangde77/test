Kemalyst::Application.config do |config|
  # Set the binding host ip address.  Defaults to "0.0.0.0"
  # config.host = "0.0.0.0"

  # Set the port.  Defaults to 3000.
  # config.port = 3000

  # Configure reuse_port option
  config.reuse_port = true

  # Disabled logging handler
  config.handlers = [] of HTTP::Handler
  config.handlers << Kemalyst::Handler::Error.instance
  config.handlers << Kemalyst::Handler::Static.instance
  config.handlers << Kemalyst::Handler::Session.instance
  config.handlers << Kemalyst::Handler::Flash.instance
  config.handlers << Kemalyst::Handler::Params.instance
  config.handlers << Kemalyst::Handler::Router.instance
end
