"""
This module provides custom manager methods for annotating files with counts of other files
that have the same size or hash.

Classes:
    FileManager: Custom manager with methods to annotate files with same size and hash counts.
"""

from django.db import models


from django.db.models import Q, F, Value, Func, OuterRef, Count, Subquery, Sum
from django.db.models.functions import Length, Replace


# Define a custom function to count occurrences of '/'
class CountChar(Func):
    function = 'LENGTH'  # SQL LENGTH function for strings
    template = '(%(function)s(%(expressions)s) - %(function)s(REPLACE(%(expressions)s, "/", "")))'


class DirectoryQuerySet(models.QuerySet):
    def annotate_is_open(self, selected_path):
        """
        Annotates each directory with a boolean indicating if the directory is open based on the selected path.

        Args:
            selected_path (str): The path to check if the directory is open.

        Returns:
            QuerySet: A QuerySet with the additional annotation `is_open`.
        """
        segments = selected_path.split('/')
        open_directories = [
            "",
            *["/".join(segments[:i + 1]) for i in range(len(segments))]
        ]
        return self.annotate(
            is_open=models.Case(
                models.When(path__in=open_directories, then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )

    def annotate_depth(self):
        """
        Annotates each directory with the depth of the directory in the tree.

        Returns:
            QuerySet: A QuerySet with the additional annotation `depth`.
        """
        return self.annotate(depth=models.Case(
            models.When(path='', then=Value(0)),
            default=Length('path') - Length(Replace('path', Value('/'))) + Value(1),
            output_field=models.IntegerField()
        ))


class FileQuerySet(models.QuerySet):
    def annotate_same_size_count(self):
        """
        Annotates each file with the count of other files that have the exact same size.

        Returns:
            QuerySet: A QuerySet with the additional annotation `same_size_count`.
        """
        subquery = self.model.objects.filter(
            size=OuterRef('size'),
            directory__tree=OuterRef('directory__tree'),
        ).values('size').annotate(
            count=Count('id')
        ).values('count')
        return self.annotate(same_size_count=Subquery(subquery))

    def annotate_same_hash_count(self):
        """
        Annotates each file with the count of other files that have the exact same hash.

        Returns:
            QuerySet: A QuerySet with the additional annotation `same_hash_count`.
        """
        subquery = self.model.objects.filter(
            hash=OuterRef('hash'),
            directory__tree=OuterRef('directory__tree'),
        ).values('hash').annotate(
            count=Count('id')
        ).values('count')
        return self.annotate(same_hash_count=Subquery(subquery))

    def annotate_depth(self):
        return self.annotate(depth=models.Case(
            models.When(directory__path='', then=Value(0)),
            default=Length('directory__path') - Length(Replace('directory__path', Value('/'))) + Value(2),
            output_field=models.IntegerField()
        ))



class FilesystemEntityManager(models.Manager):
    def annotate_same_size_count(self):
        """
        Annotates each file with the count of other files that have the exact same size.

        Returns:
            QuerySet: A QuerySet with the additional annotation `same_size_count`.
        """
        return self.annotate(
            same_size_count=models.Count(
                'size',
                filter=models.Q(size=models.OuterRef('size'))
            )
        )

    def annotate_same_hash_count(self):
        """
        Annotates each file with the count of other files that have the exact same hash.

        Returns:
            QuerySet: A QuerySet with the additional annotation `same_hash_count`.
        """
        return self.annotate(
            same_hash_count=models.Count(
                'hash',
                filter=models.Q(hash=models.OuterRef('hash'))
            )
        )


class DirectoryManager(models.Manager):
    def get_queryset(self):
        return DirectoryQuerySet(self.model, using=self._db)

    '''
    def annotate_total_size(self):
        """
        Annotates each directory with the total size of all files whose path starts with the path of this directory.

        Returns:
            QuerySet: A QuerySet with the additional annotation `total_size`.
        """
        return self.annotate(
            total_size=models.Sum(
                'files__size',
                filter=models.Q(files__directory__path__startswith=models.OuterRef('path'))
            )
        )

    def annotate_directory_hashes(self):
        """
        Annotates each directory with a combined hash of all files within the directory and its subdirectories.

        Returns:
            QuerySet: A QuerySet with the additional annotation `combined_hash`.
        """
        breakpoint()
        return self.annotate(
            combined_hash=models.Subquery(
                File.objects.filter(
                    directory__path__startswith=models.OuterRef('path')
                ).values('directory').annotate(
                    combined_hash=models.Func(
                        models.F('hash'),
                        function='string_agg',
                        template="%(function)s(%(expressions)s, '')"
                    )
                ).values('combined_hash')[:1]
            )
        )

    def get_queryset(self):
        """
        Annotates each directory with the depth of the directory in the tree.

        Returns:
            QuerySet: A QuerySet with the additional annotation `depth`.
        """
        qs = super().get_queryset()


        #qs = qs.annotate(depth=Length('path') - Length(Replace('path', Value('/'))))
        qs = qs.annotate(depth=models.Case(
            models.When(path='', then=Value(0)),
            default=Length('path') - Length(Replace('path', Value('/'))) + Value(1),
            output_field=models.IntegerField()
        ))
        return qs

    def annotate_is_open(self, selected_path):
        """
        Annotates each directory with a boolean indicating if the directory is open based on the selected path.

        Args:
            selected_path (str): The path to check if the directory is open.

        Returns:
            QuerySet: A QuerySet with the additional annotation `is_open`.
        """
        #open_directories = (f"{x}" for x in selected_path.split('/'))
        segments = selected_path.split('/')
        open_directories = [
            "",
            *["/".join(segments[:i + 1]) for i in range(len(segments))]
        ]
        return self.annotate(
            is_open=models.Case(
                models.When(path__in=open_directories, then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )
    '''


class FileManager(models.Manager):
    def get_queryset(self):
        return FileQuerySet(self.model, using=self._db)
