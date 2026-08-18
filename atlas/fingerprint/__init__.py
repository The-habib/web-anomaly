"""
Project Atlas — Multi-Dimensional Fingerprint Subsystem.
"""

from atlas.fingerprint.structure import HtmlStructureFingerprint, compute_structure_fingerprint
from atlas.fingerprint.technology import TechnologyFingerprint, compute_technology_fingerprint
from atlas.fingerprint.visual import VisualLayoutFingerprint, compute_visual_fingerprint
from atlas.fingerprint.engine import UnifiedFingerprint, generate_unified_fingerprint, save_fingerprints, FINGERPRINT_VERSION
