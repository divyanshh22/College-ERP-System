from django.apps import AppConfig


class InfoConfig(AppConfig):
    name = 'info'

    def ready(self):
        try:
            from django.db import connection
            if 'info_attendance' in connection.introspection.table_names():
                from django.contrib.auth import get_user_model
                if not get_user_model().objects.filter(username='admin').exists():
                    from django.core.management import call_command
                    call_command('seed_data', no_attendance=True)
        except Exception as exc:
            import sys
            sys.stderr.write('[startup] demo data seed skipped: %s\n' % exc)
