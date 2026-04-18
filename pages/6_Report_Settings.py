"""Report Settings — configure branding/signature for generated reports."""
import streamlit as st

try:
    from branding import BrandingSettings, load_settings, save_settings, clear_settings
    _HAS_BRANDING = True
except Exception:
    _HAS_BRANDING = False

import storage
from ui import hero, inject_css, footer, section_title, divider, callout

st.set_page_config(page_title="EduPulse — Report Settings", page_icon="⚙️", layout="wide")
inject_css()
hero("Report Settings")

st.write(
    "Configure the branding and signature block that appears in downloaded reports (PDFs). "
    "These settings live in your current session and are applied to every report you generate."
)

if not _HAS_BRANDING:
    st.info(
        "Branding module not available in this build. Values entered below are stored in "
        "session state only and may not flow into generated PDFs."
    )

    ss = st.session_state.setdefault("branding_fallback", {})
    with st.form("branding_form_fallback"):
        ss["copyright_owner_name"] = st.text_input("Copyright owner name", value=ss.get("copyright_owner_name", ""))
        ss["authorized_signature_name"] = st.text_input("Authorized signatory name", value=ss.get("authorized_signature_name", ""))
        ss["designation"] = st.text_input("Designation (optional)", value=ss.get("designation", ""))
        ss["institution_name"] = st.text_input("Institution name", value=ss.get("institution_name", ""))
        ss["footer_note"] = st.text_area("Footer note", value=ss.get("footer_note", ""), height=80)
        submitted = st.form_submit_button("💾 Save settings", type="primary", use_container_width=True)
    if submitted:
        st.success("Settings saved for this session.")
    footer()
    st.stop()


current = load_settings()

with st.form("branding_form", clear_on_submit=False):
    section_title("Ownership & institution")
    c1, c2 = st.columns(2)
    with c1:
        owner = st.text_input(
            "Copyright owner name",
            value=current.copyright_owner_name,
            help="Appears in the footer as © <Owner>.",
        )
        institution = st.text_input(
            "Institution name",
            value=current.institution_name,
            help="Appears in the subtitle/cover of reports.",
        )
    with c2:
        signer = st.text_input(
            "Authorized signatory name",
            value=current.authorized_signature_name,
            help="Shown under the signature line. If no image is uploaded, this name is shown as the signature.",
        )
        desig = st.text_input(
            "Designation (optional)",
            value=current.designation,
            help="E.g., 'Manager, Office of Quality Initiatives'.",
        )

    section_title("Signature image (optional)")
    sig_file = st.file_uploader(
        "Upload signature PNG/JPG",
        type=["png", "jpg", "jpeg"],
        help="Recommended: transparent PNG, ~400×160 px. Leave empty to use the typed name.",
    )
    remove_sig = st.checkbox(
        "Remove the existing signature image",
        value=False,
        help="Tick and click Save to delete the currently stored signature image.",
    )

    if current.has_signature_image():
        st.caption("Current signature image is set ✓")
    else:
        st.caption("No signature image on file.")

    section_title("Footer note (optional)")
    footer_note = st.text_area(
        "Footer text",
        value=current.footer_note,
        help="Appears on the left side of the signature block. Keep it short.",
        height=80,
    )

    c_save, c_clear = st.columns([1, 1])
    save = c_save.form_submit_button("💾 Save settings", type="primary", use_container_width=True)
    clear = c_clear.form_submit_button("🗑 Reset to defaults", use_container_width=True)

if save:
    new_settings = BrandingSettings(
        copyright_owner_name=owner.strip(),
        authorized_signature_name=signer.strip(),
        designation=desig.strip(),
        institution_name=institution.strip(),
        footer_note=footer_note.strip(),
        signature_image_bytes=None if remove_sig else current.signature_image_bytes,
        signature_image_type=None if remove_sig else current.signature_image_type,
    )
    if sig_file is not None and not remove_sig:
        new_settings.signature_image_bytes = sig_file.read()
        new_settings.signature_image_type = sig_file.type
    save_settings(new_settings)
    for ws in storage.all_workspaces():
        ws.internal_pdf_bytes = None
        ws.external_pdf_bytes = None
    st.success("Saved. Previously generated PDFs will be regenerated next time you download them.")
    st.rerun()

if clear:
    clear_settings()
    for ws in storage.all_workspaces():
        ws.internal_pdf_bytes = None
        ws.external_pdf_bytes = None
    st.success("Reset to defaults.")
    st.rerun()

divider()
section_title("Current settings")
display = current.to_dict_safe()
if not any(display.get(k) for k in ["copyright_owner_name", "authorized_signature_name",
                                      "designation", "institution_name", "footer_note"]) \
   and not current.has_signature_image():
    callout("No branding configured yet — reports will use the default EduPulse styling.")
else:
    st.json(display)

footer()
