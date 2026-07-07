"""PyInstaller runtime hook: make importlib.metadata find bundled dist-info."""
import sys
import pathlib
import importlib.metadata as _ilm

_internal = pathlib.Path(sys.executable).parent / '_internal'
sys.path.insert(0, str(_internal))

if _internal.is_dir():
    _orig_version = _ilm.version
    def _patched_version(name):
        try:
            return _orig_version(name)
        except _ilm.PackageNotFoundError:
            norm = name.lower().replace('-', '_')
            for _d in _internal.glob('*.dist-info'):
                pkg = _d.name.split('-')[0].lower().replace('-', '_')
                if pkg == norm:
                    return _ilm.PathDistribution(_d).version
            raise
    _ilm.version = _patched_version
