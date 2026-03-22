from django.apps import AppConfig
import os

class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        # சர்வர் ரெண்டு வாட்டி ரன் ஆகுறத தடுக்க இந்த 'RUN_MAIN' செக் பண்றோம்
        if os.environ.get('RUN_MAIN'):
            from . import updater
            updater.start()