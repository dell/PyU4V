# version.py
# Single source of truth for all PyU4V/Unisphere version information.

# --- PyU4V package version (PyPI / __version__) ---
MAJOR_VERSION = '10.5'   # marketing / major SDK version
VERSION = '10.5.0.1'     # full PyU4V package version

# --- Unisphere REST API version ---
# API_VERSION is the value placed in REST URL paths. It is exposed as
# constants.UNISPHERE_VERSION and resolved at runtime via common.UNI_VERSION.
API_VERSION = "105"
# Enhanced (v-prefixed) REST API version used by the enhanced endpoints.
ENHANCED_API_VERSION = 'v1'
