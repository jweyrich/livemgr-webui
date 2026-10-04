#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Django 1.4 deprecates execute_manager, which imported the project's
    # package from its parent directory. Put that directory on the path so
    # `webui` imports, after this one so --settings=settings_<name> still works.
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webui.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
