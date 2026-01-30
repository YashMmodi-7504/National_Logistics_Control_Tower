"""
EVIDENCE EXPORTER

Purpose:
- Export snapshots as legal evidence
- Include verification data
- Court-defensible format

Requirements:
- JSON + CSV export
- Include: payload, hash, signature, chain proof
- Verification instructions
- Offline verifiable
"""

import json
import csv
import zipfile
import io
import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.snapshot_store import read_snapshot
from app.security.tamper_detector import detect_snapshot_tampering
from app.security.snapshot_hasher import hash_snapshot
from app.forensics.replay_engine import replay_snapshot_state
from app.forensics.incident_timeline import build_incident_timeline, export_timeline_text


class EvidenceExportError(Exception):
    """Raised when evidence export fails."""
    pass


def export_evidence(
    snapshot_name: str,
    format: str = "zip",
    include_timeline: bool = True,
) -> bytes:
    """
    Export snapshot as legal evidence package.
    
    Args:
        snapshot_name: Name of snapshot to export
        format: Export format ("zip", "json", "csv")
        include_timeline: Include incident timeline
    
    Returns:
        Bytes of exported evidence
    
    Raises:
        EvidenceExportError: If export fails
    
    Package Contents:
        - snapshot_payload.json: The snapshot content
        - snapshot_metadata.json: Hash, signature, chain info
        - integrity_report.json: Tamper detection results
        - verification_instructions.txt: How to verify offline
        - timeline.txt: Incident timeline (if requested)
    """
    if format not in ["zip", "json", "csv"]:
        raise EvidenceExportError(f"Unsupported format: {format}")
    
    # Read snapshot
    snapshot = read_snapshot(snapshot_name)
    if snapshot is None:
        raise EvidenceExportError(f"Snapshot not found: {snapshot_name}")
    
    # Run integrity check
    integrity_result = detect_snapshot_tampering(snapshot_name)
    
    # Generate evidence package
    if format == "zip":
        return _export_as_zip(
            snapshot_name,
            snapshot,
            integrity_result,
            include_timeline,
        )
    elif format == "json":
        return _export_as_json(
            snapshot_name,
            snapshot,
            integrity_result,
            include_timeline,
        )
    else:
        return _export_as_csv(
            snapshot_name,
            snapshot,
            integrity_result,
        )


def _export_as_zip(
    snapshot_name: str,
    snapshot: Dict[str, Any],
    integrity_result: Dict[str, Any],
    include_timeline: bool,
) -> bytes:
    """Export as ZIP archive with all verification materials."""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Snapshot payload
        payload_json = json.dumps(snapshot, indent=2, ensure_ascii=False)
        zf.writestr(
            f"{snapshot_name}/snapshot_payload.json",
            payload_json
        )
        
        # 2. Metadata
        metadata = _build_metadata(snapshot_name, snapshot, integrity_result)
        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
        zf.writestr(
            f"{snapshot_name}/snapshot_metadata.json",
            metadata_json
        )
        
        # 3. Integrity report
        integrity_json = json.dumps(integrity_result, indent=2, ensure_ascii=False)
        zf.writestr(
            f"{snapshot_name}/integrity_report.json",
            integrity_json
        )
        
        # 4. Verification instructions
        instructions = _generate_verification_instructions(snapshot_name)
        zf.writestr(
            f"{snapshot_name}/verification_instructions.txt",
            instructions
        )
        
        # 5. Timeline (if requested)
        if include_timeline:
            timeline = build_incident_timeline(snapshot_name)
            timeline_text = export_timeline_text(timeline)
            zf.writestr(
                f"{snapshot_name}/incident_timeline.txt",
                timeline_text
            )
        
        # 6. Chain proof (if available)
        chain_proof = _get_chain_proof(snapshot_name)
        if chain_proof:
            chain_json = json.dumps(chain_proof, indent=2, ensure_ascii=False)
            zf.writestr(
                f"{snapshot_name}/chain_proof.json",
                chain_json
            )
        
        # 7. Export manifest
        manifest = _build_manifest(
            snapshot_name,
            include_timeline,
            chain_proof is not None,
        )
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
        zf.writestr(
            f"{snapshot_name}/manifest.json",
            manifest_json
        )
    
    buffer.seek(0)
    return buffer.read()


def _export_as_json(
    snapshot_name: str,
    snapshot: Dict[str, Any],
    integrity_result: Dict[str, Any],
    include_timeline: bool,
) -> bytes:
    """Export as single JSON file."""
    evidence = {
        "snapshot_name": snapshot_name,
        "export_timestamp": datetime.now().isoformat(),
        "snapshot_payload": snapshot,
        "metadata": _build_metadata(snapshot_name, snapshot, integrity_result),
        "integrity_report": integrity_result,
    }
    
    if include_timeline:
        timeline = build_incident_timeline(snapshot_name)
        evidence["timeline"] = [entry.to_dict() for entry in timeline]
    
    json_str = json.dumps(evidence, indent=2, ensure_ascii=False)
    return json_str.encode('utf-8')


def _export_as_csv(
    snapshot_name: str,
    snapshot: Dict[str, Any],
    integrity_result: Dict[str, Any],
) -> bytes:
    """Export as CSV (metadata only, not full payload)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Header
    writer.writerow(["Field", "Value"])
    
    # Metadata
    writer.writerow(["Snapshot Name", snapshot_name])
    writer.writerow(["Export Time", datetime.now().isoformat()])
    
    metadata = _build_metadata(snapshot_name, snapshot, integrity_result)
    writer.writerow(["Content Hash", metadata.get("content_hash")])
    writer.writerow(["Signature", metadata.get("signature")])
    writer.writerow(["Timestamp", metadata.get("timestamp")])
    
    # Integrity
    writer.writerow(["Integrity Status", integrity_result.get("status")])
    writer.writerow(["Severity", integrity_result.get("severity", "N/A")])
    
    csv_str = buffer.getvalue()
    return csv_str.encode('utf-8')


def _build_metadata(
    snapshot_name: str,
    snapshot: Dict[str, Any],
    integrity_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Build complete metadata for evidence."""
    content_hash = hash_snapshot(snapshot)
    
    # Read stored metadata if exists
    stored_metadata = _read_stored_metadata(snapshot_name)
    
    return {
        "snapshot_name": snapshot_name,
        "content_hash": content_hash,
        "signature": stored_metadata.get("signature") if stored_metadata else None,
        "timestamp": snapshot.get("generated_at"),
        "size_bytes": len(json.dumps(snapshot)),
        "integrity_status": integrity_result.get("status"),
        "violated_rules": integrity_result.get("violated_rules", []),
    }


def _generate_verification_instructions(snapshot_name: str) -> str:
    """Generate human-readable verification instructions."""
    instructions = f"""
EVIDENCE VERIFICATION INSTRUCTIONS
==================================

Snapshot Name: {snapshot_name}
Export Date: {datetime.now().isoformat()}

OFFLINE VERIFICATION STEPS:

1. VERIFY HASH
   - Open: snapshot_payload.json
   - Compute SHA-256 hash
   - Compare with: snapshot_metadata.json -> content_hash
   - Command: sha256sum snapshot_payload.json

2. VERIFY SIGNATURE
   - Requires signing key (SNAPSHOT_SIGNING_KEY)
   - Compute HMAC-SHA256 of content_hash
   - Compare with: snapshot_metadata.json -> signature
   - Command: echo -n "<hash>" | openssl dgst -sha256 -hmac "<key>"

3. VERIFY CHAIN
   - Open: chain_proof.json (if present)
   - Verify each entry links to previous
   - First entry must reference GENESIS

4. VERIFY INTEGRITY
   - Check: integrity_report.json
   - Status must be "INTACT"
   - violated_rules must be empty

REQUIRED TOOLS:
- sha256sum or equivalent
- openssl (for HMAC verification)
- JSON parser (jq, python, etc.)

CHAIN OF CUSTODY:
- Exported by: System
- Export timestamp: {datetime.now().isoformat()}
- Snapshot timestamp: (see metadata)

For questions or disputes, contact system administrator.
"""
    return instructions


def _get_chain_proof(snapshot_name: str) -> Optional[Dict[str, Any]]:
    """Get chain proof for snapshot if available."""
    # This would read from hash chain store
    # For now, return None (not yet implemented)
    return None


def _build_manifest(
    snapshot_name: str,
    includes_timeline: bool,
    includes_chain: bool,
) -> Dict[str, Any]:
    """Build export manifest."""
    return {
        "snapshot_name": snapshot_name,
        "export_timestamp": datetime.now().isoformat(),
        "format": "evidence_package",
        "version": "1.0",
        "contents": {
            "snapshot_payload": True,
            "metadata": True,
            "integrity_report": True,
            "verification_instructions": True,
            "timeline": includes_timeline,
            "chain_proof": includes_chain,
        },
    }


def _read_stored_metadata(snapshot_name: str) -> Optional[Dict[str, Any]]:
    """Read stored metadata for snapshot."""
    metadata_dir = os.path.join("data", "snapshots", "metadata")
    metadata_path = os.path.join(metadata_dir, f"{snapshot_name}_meta.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def export_multiple_snapshots(
    snapshot_names: list,
    include_timeline: bool = True,
) -> bytes:
    """
    Export multiple snapshots as a single evidence package.
    
    Args:
        snapshot_names: List of snapshot names
        include_timeline: Include timelines
    
    Returns:
        ZIP archive bytes containing all snapshots
    """
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for snapshot_name in snapshot_names:
            try:
                # Export individual snapshot
                snapshot_zip = export_evidence(
                    snapshot_name,
                    format="zip",
                    include_timeline=include_timeline,
                )
                
                # Extract and add to combined archive
                with zipfile.ZipFile(io.BytesIO(snapshot_zip), 'r') as snapshot_zf:
                    for file_info in snapshot_zf.filelist:
                        content = snapshot_zf.read(file_info.filename)
                        zf.writestr(file_info.filename, content)
            
            except EvidenceExportError:
                # Add error file for failed exports
                zf.writestr(
                    f"{snapshot_name}/export_failed.txt",
                    f"Failed to export snapshot: {snapshot_name}"
                )
    
    buffer.seek(0)
    return buffer.read()
