"""
Session-state backed storage for CaseWorkspace objects.

No server-side persistence. Collisions by name are resolved by replacement.
Legacy `add_case` / `get_case` / `all_cases` names preserved.
"""
from __future__ import annotations

from typing import List, Optional
import streamlit as st


_KEY = "workspaces"


def _ensure():
    if _KEY not in st.session_state:
        st.session_state[_KEY] = []
    # legacy alias kept so older imports do not crash
    if "cases" not in st.session_state:
        st.session_state["cases"] = st.session_state[_KEY]


def add_workspace(ws) -> None:
    _ensure()
    st.session_state[_KEY] = [w for w in st.session_state[_KEY] if w.name != ws.name]
    st.session_state[_KEY].append(ws)
    st.session_state["cases"] = st.session_state[_KEY]


def all_workspaces() -> List:
    _ensure()
    return list(st.session_state[_KEY])


def get_workspace(name: str):
    for w in all_workspaces():
        if w.name == name:
            return w
    return None


def remove_workspace(name: str) -> None:
    _ensure()
    st.session_state[_KEY] = [w for w in st.session_state[_KEY] if w.name != name]
    st.session_state["cases"] = st.session_state[_KEY]


def rename_workspace(old_name: str, new_name: str) -> bool:
    ws = get_workspace(old_name)
    if not ws or not new_name.strip():
        return False
    # avoid collision
    if get_workspace(new_name) and new_name != old_name:
        return False
    ws.name = new_name.strip()
    return True


def clear_all() -> None:
    st.session_state[_KEY] = []
    st.session_state["cases"] = []


# ---------------------------------------------------------------------------
# Legacy aliases (older code imports these)
# ---------------------------------------------------------------------------
add_case = add_workspace
all_cases = all_workspaces
get_case = get_workspace
remove_case = remove_workspace
