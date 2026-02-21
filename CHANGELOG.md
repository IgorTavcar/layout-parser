# Changelog

## 0.4.0 (2026-02-21)

### Breaking changes

- Require Python >= 3.12
- Replace `iopath` dependency with `pooch`
- Remove Dropbox URL support; all model weights served from HuggingFace
- Require `google-cloud-vision >= 3.1` (was pinned to `==1`)
- Unpin `paddlepaddle` (now `>= 2.1.0`)

### Migrated to modern tooling

- Switch from `setup.py` / `setup.cfg` to `pyproject.toml` with Hatch build backend
- Native `uv` support for dependency management

### Bug fixes

- Fix `load_csv` / `load_dataframe` crash with newer pandas (`pd.isna` on list values, `StringDtype` detection)
- Fix GCV agent for google-cloud-vision v3+ API (`_vision.types.X` -> `_vision.X`, proto-plus JSON serialization)
- Fix detectron2 model loading with torch >= 2.6 (`weights_only=True` default)
- Update test fixture config to use HuggingFace URL (replaces dead Dropbox link)
- Regenerate tesseract pickle fixture for current NumPy

### Improvements

- Make OCR imports conditional (no crash when `google-cloud-vision` or `pytesseract` not installed)
- Add `pytest.mark.skipif` guards for all optional-dependency tests
- Remove Python < 3.8 compatibility shim in `file_utils.py`
