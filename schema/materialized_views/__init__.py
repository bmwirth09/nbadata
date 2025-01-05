from . import views
from .registry import instances
from django.db.utils import ProgrammingError

def create_instances():
    for instance in instances:
        try:
            instance.create()
        except Exception as e:
            print(instance.__class__.__name__)
            raise e

def refresh_instances(force=True):
    for instance in instances:
        if force:
            try:
                instance.refresh()
            except ProgrammingError as e:
                if 'does not exist' in e.message:
                    instance.create()
                else:
                    raise e
        else:
            instance.refresh()

def delete_instances(force=True):
    for instance in reversed(instances):
        if force:
            try:
                instance.delete()
            except Exception:
                pass
        else:
            instance.delete()


def recreate_instances():
    delete_instances()
    create_instances()