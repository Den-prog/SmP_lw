from django.apps import AppConfig


class WebPanelConfig(AppConfig):
    name = 'web_panel'
    
    def ready(self):
        import web_panel.signals

