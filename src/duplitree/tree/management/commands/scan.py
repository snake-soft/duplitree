from django.core.management.base import BaseCommand
from tree.models import Tree, File, Directory


class Command(BaseCommand):
    help = 'Scan filesystem for files and directories'

    def handle(self, *args, **kwargs):
        tree = Tree.objects.create(base_path="/mnt")
        tree.scan()
        qs = File.objects.filter(directory__tree=tree)
        for file in qs:
            file.read_metadata()
        qs = qs.annotate_same_size_count()
        for file in qs.filter(same_size_count__gt=1):
            file.hash_file()
