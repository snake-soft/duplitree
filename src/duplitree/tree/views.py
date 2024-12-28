from django.db.models.functions import Replace, Length
from django.views.generic import DetailView, ListView, DeleteView
from django.db.models import OuterRef, Subquery, Count, Q, Value
from .models import Tree, File
from django.db import models


class TreeListView(ListView):
    model = Tree


class TreeDetailView(DetailView):
    model = Tree

    def get_context_data(self, **kwargs):
        selected_path = self.kwargs.get('path', "")
        depth = selected_path.count('/')
        if selected_path:
            depth += 1
        return {
            **super().get_context_data(**kwargs),
            "directories": self.get_directory_queryset(selected_path),
            "files": self.get_file_queryset(selected_path),
            "selected_path": selected_path,
            "depth": depth,
            "show_depth": depth + 1,
        }

    def get_directory_queryset(self, selected_path):
        qs = self.object.directories.all()
        qs = qs.annotate_is_open(selected_path)
        qs = qs.annotate_depth()
        #qs = qs.annotate_size()
        return qs

    def get_file_queryset(self, selected_path):
        qs = File.objects.filter(
            directory__tree=self.object,
            directory__path=selected_path,
        )
        qs = qs.annotate_depth()
        qs = qs.annotate_same_hash_count()
        return qs

class TreePathView(TreeDetailView):
    pass


class FileDetailView(DetailView):
    model = File
    template_name = "tree/file_modal.html"

class FileDeleteView(DeleteView):
    model = File
