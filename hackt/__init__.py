def create_app(default_type='production'):
    from hackt.views import app
    app.config.from_object('hackt.config.Config')
    return app