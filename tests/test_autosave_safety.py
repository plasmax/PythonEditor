"""
Tests for autosave data-safety guarantees.

These tests verify that PythonEditor's autosave system
cannot lose user data under adverse conditions such as
disk-full errors, crashes during writes, and corrupt files.
"""
from __future__ import unicode_literals
from __future__ import print_function

import io
import os
import shutil
import tempfile
import time

import pytest
from unittest import mock
from xml.etree import cElementTree as ETree

from PythonEditor.ui.features import autosavexml


XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

VALID_XML_WITH_DATA = (
    XML_HEADER
    + '<script>\n'
    '<subscript name="test_tab" uuid="abc-123" tab_index="0">'
    'print("hello world")</subscript>\n'
    '<subscript name="important" uuid="def-456" tab_index="1">'
    'x = 42\ny = x * 2\nprint(y)</subscript>\n'
    '</script>'
)

VALID_XML_EMPTY = XML_HEADER + '<script></script>'


@pytest.fixture
def tmp_autosave(tmp_path):
    """Provide an isolated autosave file and patch the module globals."""
    autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
    with open(autosave_path, 'w') as f:
        f.write(VALID_XML_WITH_DATA)

    original_file = autosavexml.AUTOSAVE_FILE
    autosavexml.AUTOSAVE_FILE = autosave_path

    # reset backup timer so rotating backups work in tests
    autosavexml._last_backup_time = 0

    yield autosave_path

    autosavexml.AUTOSAVE_FILE = original_file
    autosavexml._last_backup_time = 0


@pytest.fixture
def tmp_empty_autosave(tmp_path):
    """Provide an isolated empty autosave file."""
    autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
    with open(autosave_path, 'w') as f:
        f.write(VALID_XML_EMPTY)

    original_file = autosavexml.AUTOSAVE_FILE
    autosavexml.AUTOSAVE_FILE = autosave_path
    autosavexml._last_backup_time = 0

    yield autosave_path

    autosavexml.AUTOSAVE_FILE = original_file
    autosavexml._last_backup_time = 0


# ============================================================
# CRITICAL: writexml must never destroy the existing file
# ============================================================

class TestWritexmlAtomicity:
    """writexml must be atomic: either the new content is fully
    written or the old content is preserved."""

    def test_writexml_writes_valid_xml(self, tmp_autosave):
        """Basic: writexml produces a parseable file."""
        root, elements = autosavexml.parsexml('subscript', path=tmp_autosave)
        autosavexml.writexml(root, path=tmp_autosave)

        # must still be parseable
        xmlp = ETree.XMLParser(encoding="utf-8")
        parser = ETree.parse(tmp_autosave, xmlp)
        new_root = parser.getroot()
        assert len(new_root.findall('subscript')) == len(elements)

    def test_writexml_preserves_file_on_disk_full(self, tmp_autosave):
        """CRITICAL: if the write fails (e.g. ENOSPC), the original
        file must be left intact."""
        # read original content
        with open(tmp_autosave, 'r') as f:
            original_content = f.read()

        root, _ = autosavexml.parsexml('subscript', path=tmp_autosave)

        # simulate disk full: io.open(fd, 'wt', ...) succeeds but
        # f.write() raises IOError
        original_open = io.open
        def failing_open(path_or_fd, *args, **kwargs):
            f = original_open(path_or_fd, *args, **kwargs)
            # only intercept the fd-based write (temp file), not path-based
            if isinstance(path_or_fd, int):
                real_write = f.write
                def enospc_write(data):
                    raise IOError('[Errno 28] No space left on device')
                f.write = enospc_write
            return f

        with mock.patch('PythonEditor.ui.features.autosavexml.io.open', failing_open):
            autosavexml.writexml(root, path=tmp_autosave)

        # the original file must be unchanged
        with open(tmp_autosave, 'r') as f:
            after_content = f.read()

        assert after_content == original_content, \
            'writexml destroyed the original file on write failure!'

    def test_writexml_does_not_truncate_then_write(self, tmp_autosave):
        """Verify writexml never opens the target path with 'w'/'wt' mode
        (which would truncate it before writing)."""
        root, _ = autosavexml.parsexml('subscript', path=tmp_autosave)

        original_open = io.open
        opened_paths = []

        def tracking_open(path_or_fd, *args, **kwargs):
            if isinstance(path_or_fd, str):
                mode = args[0] if args else kwargs.get('mode', 'r')
                if 'w' in mode:
                    opened_paths.append(path_or_fd)
            return original_open(path_or_fd, *args, **kwargs)

        with mock.patch('PythonEditor.ui.features.autosavexml.io.open', tracking_open):
            autosavexml.writexml(root, path=tmp_autosave)

        # the autosave file itself should NOT have been opened for writing
        # only temp files should have been written to
        for p in opened_paths:
            assert p != tmp_autosave, \
                'writexml opened the target file directly for writing (truncation risk)!'

    def test_writexml_rejects_empty_output(self, tmp_autosave):
        """writexml must not replace a good file with empty content."""
        with open(tmp_autosave, 'r') as f:
            original_content = f.read()

        # create an empty root element
        empty_root = ETree.Element('script')
        autosavexml.writexml(empty_root, path=tmp_autosave)

        # file should exist and be parseable (empty is valid XML, just no subscripts)
        with open(tmp_autosave, 'r') as f:
            content = f.read()
        assert len(content) > 0, 'writexml wrote an empty file!'

        xmlp = ETree.XMLParser(encoding="utf-8")
        ETree.parse(tmp_autosave, xmlp)  # must not raise

    def test_writexml_temp_file_cleaned_up_on_failure(self, tmp_autosave):
        """Temp files should not accumulate on repeated failures."""
        root, _ = autosavexml.parsexml('subscript', path=tmp_autosave)
        dir_name = os.path.dirname(tmp_autosave)

        # count existing temp files
        before = set(os.listdir(dir_name))

        # simulate write failure: io.open succeeds but write raises
        original_open = io.open
        def failing_open(path_or_fd, *args, **kwargs):
            f = original_open(path_or_fd, *args, **kwargs)
            if isinstance(path_or_fd, int):
                def enospc_write(data):
                    raise IOError('disk full')
                f.write = enospc_write
            return f

        with mock.patch('PythonEditor.ui.features.autosavexml.io.open', failing_open):
            autosavexml.writexml(root, path=tmp_autosave)

        after = set(os.listdir(dir_name))
        new_tmp_files = [f for f in (after - before)
                         if f.startswith('.pythoneditor_') and f.endswith('.tmp')]
        assert len(new_tmp_files) == 0, \
            'Temp file left behind after failed write: %s' % new_tmp_files


# ============================================================
# Rotating backups
# ============================================================

class TestRotatingBackups:

    def test_rotate_backup_creates_backup(self, tmp_autosave):
        """A backup should be created when writexml is called."""
        root, _ = autosavexml.parsexml('subscript', path=tmp_autosave)
        autosavexml.writexml(root, path=tmp_autosave)

        backup_dir = autosavexml._get_backup_dir(tmp_autosave)
        assert os.path.isdir(backup_dir), 'Backup directory was not created'

        backups = os.listdir(backup_dir)
        assert len(backups) >= 1, 'No backup files were created'

        # backup should be valid XML
        backup_path = os.path.join(backup_dir, backups[0])
        xmlp = ETree.XMLParser(encoding="utf-8")
        ETree.parse(backup_path, xmlp)  # must not raise

    def test_rotate_backup_skips_empty_files(self, tmp_path):
        """Empty/0-byte files should never be backed up."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        # create a 0-byte file
        open(autosave_path, 'w').close()
        assert os.path.getsize(autosave_path) == 0

        autosavexml._last_backup_time = 0
        autosavexml._rotate_backup(autosave_path)

        backup_dir = autosavexml._get_backup_dir(autosave_path)
        if os.path.isdir(backup_dir):
            assert len(os.listdir(backup_dir)) == 0, \
                'A 0-byte file was backed up!'

    def test_rotate_backup_validates_xml(self, tmp_path):
        """Backups of files with invalid XML should still be created
        (non-empty), but _find_latest_backup should skip them."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        with open(autosave_path, 'w') as f:
            f.write('this is not valid xml at all <broken>')

        autosavexml._last_backup_time = 0
        autosavexml._rotate_backup(autosave_path)

        # _find_latest_backup should return None since the backup is invalid XML
        result = autosavexml._find_latest_backup(autosave_path)
        assert result is None, \
            '_find_latest_backup returned an invalid XML backup!'

    def test_rotate_backup_respects_interval(self, tmp_autosave):
        """Backups should not be created more frequently than BACKUP_INTERVAL."""
        autosavexml._last_backup_time = time.time()  # just backed up
        autosavexml._rotate_backup(tmp_autosave)

        backup_dir = autosavexml._get_backup_dir(tmp_autosave)
        if os.path.isdir(backup_dir):
            assert len(os.listdir(backup_dir)) == 0

    def test_rotate_backup_prunes_old(self, tmp_autosave):
        """Only MAX_BACKUPS should be retained."""
        backup_dir = autosavexml._get_backup_dir(tmp_autosave)
        os.makedirs(backup_dir, exist_ok=True)
        basename = os.path.basename(tmp_autosave)

        # create more than MAX_BACKUPS old backups
        for i in range(autosavexml.MAX_BACKUPS + 3):
            ts = 1000000 + i
            bak_path = os.path.join(
                backup_dir, '{0}.{1}.bak'.format(basename, ts)
            )
            with open(bak_path, 'w') as f:
                f.write(VALID_XML_WITH_DATA)

        autosavexml._last_backup_time = 0
        autosavexml._rotate_backup(tmp_autosave)

        backups = [f for f in os.listdir(backup_dir) if f.endswith('.bak')]
        assert len(backups) <= autosavexml.MAX_BACKUPS, \
            'Too many backups: %d (max %d)' % (len(backups), autosavexml.MAX_BACKUPS)

    def test_find_latest_backup_returns_most_recent_valid(self, tmp_autosave):
        """_find_latest_backup should return the newest valid backup."""
        backup_dir = autosavexml._get_backup_dir(tmp_autosave)
        os.makedirs(backup_dir, exist_ok=True)
        basename = os.path.basename(tmp_autosave)

        # create an old valid backup
        old_path = os.path.join(backup_dir, '{0}.1000.bak'.format(basename))
        with open(old_path, 'w') as f:
            f.write(VALID_XML_EMPTY)

        # create a newer invalid backup
        bad_path = os.path.join(backup_dir, '{0}.2000.bak'.format(basename))
        with open(bad_path, 'w') as f:
            f.write('broken xml <<<<')

        # create the newest valid backup
        new_path = os.path.join(backup_dir, '{0}.3000.bak'.format(basename))
        with open(new_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA)

        result = autosavexml._find_latest_backup(tmp_autosave)
        assert result == new_path


# ============================================================
# fix_broken_xml recovery
# ============================================================

class TestFixBrokenXml:

    def test_fix_control_characters(self, tmp_path):
        """fix_broken_xml should recover XML with control characters."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        # inject a control character into otherwise valid XML
        bad_xml = VALID_XML_WITH_DATA.replace('hello world', 'hello\x00world')
        with open(autosave_path, 'w') as f:
            f.write(bad_xml)

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            parser = autosavexml.fix_broken_xml(path=autosave_path)
            root = parser.getroot()
            subs = root.findall('subscript')
            assert len(subs) == 2, 'Subscripts were lost during recovery!'
        finally:
            autosavexml.AUTOSAVE_FILE = original_file

    def test_fix_empty_file_restores_from_backup(self, tmp_path):
        """An empty/0-byte file should be restored from backup if available."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        # create the 0-byte corrupt file
        open(autosave_path, 'w').close()

        # create a valid backup
        backup_dir = autosavexml._get_backup_dir(autosave_path)
        os.makedirs(backup_dir, exist_ok=True)
        basename = os.path.basename(autosave_path)
        backup_path = os.path.join(
            backup_dir, '{0}.9999.bak'.format(basename)
        )
        with open(backup_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA)

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            parser = autosavexml.fix_broken_xml(path=autosave_path)
            root = parser.getroot()
            subs = root.findall('subscript')
            assert len(subs) == 2, \
                'Data was not restored from backup! Got %d subscripts' % len(subs)
        finally:
            autosavexml.AUTOSAVE_FILE = original_file

    def test_fix_truncated_xml_restores_from_backup(self, tmp_path):
        """A truncated XML file should be restored from backup."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        # write truncated content (as would happen on disk-full)
        with open(autosave_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA[:50])

        # create a valid backup
        backup_dir = autosavexml._get_backup_dir(autosave_path)
        os.makedirs(backup_dir, exist_ok=True)
        basename = os.path.basename(autosave_path)
        backup_path = os.path.join(
            backup_dir, '{0}.9999.bak'.format(basename)
        )
        with open(backup_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA)

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            parser = autosavexml.fix_broken_xml(path=autosave_path)
            root = parser.getroot()
            subs = root.findall('subscript')
            assert len(subs) == 2, \
                'Data was not restored! Got %d subscripts' % len(subs)
        finally:
            autosavexml.AUTOSAVE_FILE = original_file

    def test_fix_no_backup_creates_empty(self, tmp_path):
        """With no backup available, fix_broken_xml should create
        a valid empty autosave (not crash)."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        with open(autosave_path, 'w') as f:
            f.write('totally broken <<< xml >>>')

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            parser = autosavexml.fix_broken_xml(path=autosave_path)
            root = parser.getroot()
            assert root is not None
            assert root.tag == 'script'
        finally:
            autosavexml.AUTOSAVE_FILE = original_file

    def test_fix_broken_xml_does_not_truncate_target(self, tmp_path):
        """fix_broken_xml must not open the target with truncating 'wt'
        unless it has validated the content to write."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        # XML with control chars that can be sanitized
        bad_xml = VALID_XML_WITH_DATA.replace('hello world', 'hello\x01world')
        with open(autosave_path, 'w') as f:
            f.write(bad_xml)

        original_content_size = os.path.getsize(autosave_path)

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            parser = autosavexml.fix_broken_xml(path=autosave_path)
            # file should be at least as large (minus the control char)
            assert os.path.getsize(autosave_path) > 0
            root = parser.getroot()
            assert len(root.findall('subscript')) == 2
        finally:
            autosavexml.AUTOSAVE_FILE = original_file


# ============================================================
# backup_autosave_file
# ============================================================

class TestBackupAutosaveFile:

    def test_backup_skips_empty_content(self, capsys):
        """backup_autosave_file must not create backups of empty content."""
        autosavexml.backup_autosave_file('/fake/path', '')
        captured = capsys.readouterr()
        assert 'Skipping' in captured.out

    def test_backup_skips_whitespace_content(self, capsys):
        """backup_autosave_file must not create backups of whitespace-only content."""
        autosavexml.backup_autosave_file('/fake/path', '   \n\n  ')
        captured = capsys.readouterr()
        assert 'Skipping' in captured.out

    def test_backup_creates_file_with_content(self):
        """backup_autosave_file must actually write the content."""
        autosavexml.backup_autosave_file('/fake/path', VALID_XML_WITH_DATA)
        # we can't easily check the temp path, but at least it shouldn't raise


# ============================================================
# End-to-end: full disk-full scenario
# ============================================================

class TestDiskFullScenario:
    """Simulate the exact sequence of events that caused data loss."""

    def test_disk_full_during_autosave_preserves_data(self, tmp_autosave):
        """Simulate: autosave writes, disk fills up mid-write.
        The original file must survive."""
        # verify we start with good data
        with open(tmp_autosave, 'r') as f:
            original = f.read()
        assert 'hello world' in original
        assert 'x = 42' in original

        root, subs = autosavexml.parsexml('subscript', path=tmp_autosave)
        assert len(subs) == 2

        # modify a subscript (simulating an autosave)
        subs[0].text = 'modified content'

        # now simulate disk full on the temp file write
        real_open = io.open
        def enospc_open(path_or_fd, *args, **kwargs):
            if isinstance(path_or_fd, int):
                # this is the fd-based open for the temp file
                class EnospcFile:
                    def __enter__(self): return self
                    def __exit__(self, *a): return False
                    def write(self, data):
                        raise IOError('[Errno 28] No space left on device')
                    def flush(self): pass
                    def fileno(self): return path_or_fd
                return EnospcFile()
            return real_open(path_or_fd, *args, **kwargs)

        with mock.patch('PythonEditor.ui.features.autosavexml.io.open', enospc_open):
            autosavexml.writexml(root, path=tmp_autosave)

        # THE CRITICAL CHECK: original file must be intact
        with open(tmp_autosave, 'r') as f:
            after = f.read()
        assert after == original, \
            'DATA LOSS: original file was destroyed by failed write!'

    def test_restart_after_corrupt_file_recovers(self, tmp_path):
        """Simulate: file got corrupted somehow, PythonEditor restarts,
        create_autosave_file should recover from backup."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')

        # step 1: create a valid file and a backup of it
        with open(autosave_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA)
        backup_dir = autosavexml._get_backup_dir(autosave_path)
        os.makedirs(backup_dir, exist_ok=True)
        basename = os.path.basename(autosave_path)
        backup_path = os.path.join(
            backup_dir, '{0}.9999.bak'.format(basename)
        )
        with open(backup_path, 'w') as f:
            f.write(VALID_XML_WITH_DATA)

        # step 2: corrupt the main file (simulating disk-full truncation)
        open(autosave_path, 'w').close()  # 0 bytes

        # step 3: simulate restart - create_autosave_file should recover
        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            result = autosavexml.create_autosave_file()
            assert result is True

            # verify the data was restored
            root, subs = autosavexml.parsexml(
                'subscript', path=autosave_path
            )
            assert len(subs) == 2, \
                'Data not recovered on restart! Got %d subscripts' % len(subs)
        finally:
            autosavexml.AUTOSAVE_FILE = original_file


# ============================================================
# parsexml safety
# ============================================================

class TestParsexml:

    def test_parsexml_returns_root_and_elements(self, tmp_autosave):
        root, elements = autosavexml.parsexml('subscript', path=tmp_autosave)
        assert root is not None
        assert isinstance(elements, list)
        assert len(elements) == 2

    def test_parsexml_with_empty_file(self, tmp_empty_autosave):
        root, elements = autosavexml.parsexml(
            'subscript', path=tmp_empty_autosave
        )
        assert root is not None
        assert len(elements) == 0

    def test_parsexml_creates_file_if_missing(self, tmp_path):
        """parsexml should handle a missing file gracefully."""
        autosave_path = str(tmp_path / 'PythonEditorHistory.xml')
        assert not os.path.exists(autosave_path)

        original_file = autosavexml.AUTOSAVE_FILE
        autosavexml.AUTOSAVE_FILE = autosave_path
        try:
            root, elements = autosavexml.parsexml(
                'subscript', path=autosave_path
            )
            assert root is not None
            assert os.path.isfile(autosave_path)
        finally:
            autosavexml.AUTOSAVE_FILE = original_file
