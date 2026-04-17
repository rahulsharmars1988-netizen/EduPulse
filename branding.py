"""
Branding & signature settings.

Persisted in Streamlit session state. Not stored server-side.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Optional
import streamlit as st


@dataclass
class BrandingSettings:
    copyright_owner_name: str = ""
    authorized_signature_name: str = ""
    designation: str = ""
    institution_name: str = ""
    footer_note: str = ""
    signature_image_bytes: Optional[bytes] = None   # PNG/JPG bytes
    signature_image_type: Optional[str] = None      # mime (e.g., "image/png")

    def has_signature_image(self) -> bool:
        return bool(self.signature_image_bytes)

    def to_dict_safe(self) -> dict:
        """Dict for display — excludes raw bytes."""
        d = asdict(self)
        d.pop("signature_image_bytes", None)
        d["has_signature_image"] = self.has_signature_image()
        return d


_KEY = "branding_settings"


def load_settings() -> BrandingSettings:
    """Return current settings from session; create defaults on first access."""
    if _KEY not in st.session_state:
        st.session_state[_KEY] = BrandingSettings()
    return st.session_state[_KEY]


def save_settings(s: BrandingSettings) -> None:
    st.session_state[_KEY] = s


def clear_settings() -> None:
    st.session_state[_KEY] = BrandingSettings()
