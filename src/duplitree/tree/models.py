import hashlib
import os
from datetime import datetime
from pathlib import Path

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.timezone import make_aware, get_default_timezone
from .managers import FileManager, DirectoryManager


FA_ICON_MAPPING = {
    'pdf': 'fa-file-pdf',
    'doc': 'fa-file-word',
    'docx': 'fa-file-word',
    'xls': 'fa-file-excel',
    'xlsx': 'fa-file-excel',
    'ppt': 'fa-file-powerpoint',
    'pptx': 'fa-file-powerpoint',
    'jpg': 'fa-file-image',
    'jpeg': 'fa-file-image',
    'png': 'fa-file-image',
    'gif': 'fa-file-image',
    'txt': 'fa-file-lines',
    'zip': 'fa-file-archive',
    'rar': 'fa-file-archive',
    'mp3': 'fa-file-audio',
    'wav': 'fa-file-audio',
    'mp4': 'fa-file-video',
    'mov': 'fa-file-video',
    'avi': 'fa-file-video',
}


class HashAlgorithm(models.TextChoices):
    MD5 = 'md5', 'MD5'
    SHA1 = 'sha1', 'SHA-1'
    SHA224 = 'sha224', 'SHA-224'
    SHA256 = 'sha256', 'SHA-256'
    SHA384 = 'sha384', 'SHA-384'
    SHA512 = 'sha512', 'SHA-512'
    BLAKE2B = 'blake2b', 'BLAKE2b'
    BLAKE2S = 'blake2s', 'BLAKE2s'


class Tree(models.Model):
    algorithm = models.CharField(
        _("Algorithmus"),
        max_length=10,
        choices=HashAlgorithm.choices,
        default=HashAlgorithm.MD5,
        help_text="Wählen Sie den zugrunde liegenden Hash-Algorithmus."
    )
    base_path = models.CharField(
        max_length=1024,  # Maximal 1024 Zeichen, ausreichend für die meisten Dateisysteme
        help_text="Pfad zum Verzeichnis oder zur Datei.",
    )

    def get_hash_function(self):
        return hashlib.new(self.algorithm)

    def scan(self):
        base_path = str(self.base_path)
        for root, dirs, files in os.walk(base_path):
            rel_path = root.lstrip(base_path)
            directory = Directory.objects.get_or_create(
                tree=self,
                path=rel_path,
                name=os.path.basename(rel_path),
            )[0]
            for name in dirs:
                Directory.objects.get_or_create(
                    tree=self,
                    parent=directory,
                    path=os.path.join(rel_path, name),
                    name=name,
                )
            for name in files:
                File.objects.get_or_create(
                    directory=directory,
                    name=name,
                )

    class Meta:
        verbose_name = _("Dateibaum")
        verbose_name_plural = _("Dateibäume")


class FilesystemEntity(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=50,
    )
    size = models.BigIntegerField(
        _("Größe"),
        blank=True, null=True,
    )
    hash = models.CharField(
        _("Hash"),
        max_length=32,
        blank=True, null=True,
    )
    created = models.DateTimeField(
        _("Erstellt"),
        blank=True, null=True,
    )
    updated = models.DateTimeField(
        _("Geändert"),
        blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Directory(FilesystemEntity):
    type = 'directory'
    tree = models.ForeignKey(
        Tree,
        related_name="directories",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self",
        related_name="subdirectories",
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=50,
        blank=True,
    )
    path = models.CharField(
        _("Relativer Pfad"),
        max_length=1024,
    )
    objects = DirectoryManager()

    @property
    def absolute_path(self):
        return Path(self.tree.base_path) / self.path.lstrip('/')

    def get_absolute_url(self):
        if self.path == '':
            return reverse('tree:detail', kwargs={'pk': self.tree.pk})
        return reverse('tree:directory', kwargs={'pk':self.tree.pk, 'path': self.path.lstrip('/')})

    class Meta:
        verbose_name = _("Verzeichnis")
        verbose_name_plural = _("Verzeichnisse")
        ordering = ['path']
        unique_together = ['tree', 'path']


class File(FilesystemEntity):
    type = 'file'
    directory = models.ForeignKey(
        Directory,
        related_name="files",
        on_delete=models.CASCADE,
    )
    objects = FileManager()

    @property
    def absolute_path(self):
        return self.directory.absolute_path / self.name

    @property
    def fa_icon(self):
        extension = self.name.split('.')[-1].lower()
        return FA_ICON_MAPPING.get(extension, "fa-file")

    def read_metadata(self, save=True):
        """
        Liest die Metadaten der Datei aus und aktualisiert die entsprechenden Felder.
        """
        file_path = self.absolute_path
        file_stat = os.stat(file_path)

        self.size = file_stat.st_size
        self.created = make_aware(datetime.fromtimestamp(file_stat.st_ctime), timezone=get_default_timezone())
        self.updated = make_aware(datetime.fromtimestamp(file_stat.st_mtime), timezone=get_default_timezone())
        if save:
            self.save()

    def hash_file(self, save=True):
        """
        Berechnet den Hash-Wert der Datei und speichert ihn im Feld `hash`.
        """
        hash_function = self.directory.tree.get_hash_function()
        with open(self.absolute_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_function.update(chunk)
        self.hash = hash_function.hexdigest()
        if save:
            self.save()

        class Meta:
            verbose_name = _("Datei")
            verbose_name_plural = _("Dateien")
            unique_together = ['directory', 'name']

'''
def bulk_save(files):
    """
    Speichert eine Liste von File-Instanzen in einer Bulk-Aktion.
    """
    File.objects.bulk_update(files, ['size', 'created', 'updated'])
'''
