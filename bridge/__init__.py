"""
Bridge layer – thin helpers for orchestrating analysis and PDF generation.

The FastAPI app currently calls analysis + CPVault directly, but this module
allows future non-HTTP use (e.g., CLI tools) to share the same orchestration.
"""
