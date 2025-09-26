"""Schematron validation for MITS 5.0 business rules."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from lxml import etree
from lxml.etree import XMLSyntaxError
from lxml.isoschematron import Schematron

from mits_validator.models import Finding, FindingLevel, ValidationResult


class SchematronValidationError(Exception):
    """Schematron validation error."""

    pass


def validate_schematron(
    xml_content: str | bytes | Path,
    rules_path: Path | None = None,
) -> ValidationResult:
    """
    Validate XML content against MITS 5.0 Schematron rules.
    
    Args:
        xml_content: XML content to validate (string, bytes, or file path)
        rules_path: Path to Schematron rules file (defaults to MITS 5.0 rules)
        
    Returns:
        ValidationResult with validation findings
        
    Raises:
        SchematronValidationError: If rules loading fails
    """
    start_time = time.time()
    findings: list[Finding] = []
    
    try:
        # Load Schematron rules
        if rules_path is None:
            rules_path = Path(__file__).parent.parent.parent.parent / "rules" / "schematron" / "5.0" / "business-rules.sch"
        
        if not rules_path.exists():
            findings.append(
                Finding(
                    level=FindingLevel.INFO,
                    code="SCHEMATRON:NO_RULES_LOADED",
                    message=f"No Schematron rules found at {rules_path}",
                    rule_ref="internal://Schematron",
                )
            )
            return ValidationResult(
                level="Schematron",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )
        
        # Parse Schematron rules
        try:
            with open(rules_path, 'rb') as f:
                rules_content = f.read()
            rules_doc = etree.fromstring(rules_content)
            schematron = Schematron(rules_doc, store_report=True)
        except etree.XMLSyntaxError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="SCHEMATRON:RULES_PARSE_ERROR",
                    message=f"Failed to parse Schematron rules: {e}",
                    rule_ref="internal://Schematron",
                )
            )
            return ValidationResult(
                level="Schematron",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )
        
        # Parse XML content
        try:
            if isinstance(xml_content, (str, bytes)):
                # Parse from string/bytes
                parser = etree.XMLParser(no_network=True, resolve_entities=False)
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode('utf-8')
                xml_doc = etree.fromstring(xml_content, parser=parser)
            else:
                # Parse from file path
                parser = etree.XMLParser(no_network=True, resolve_entities=False)
                xml_doc = etree.parse(str(xml_content), parser=parser)
        except XMLSyntaxError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="SCHEMATRON:XML_PARSE_ERROR",
                    message=f"XML parsing failed: {e}",
                    rule_ref="internal://Schematron",
                )
            )
            return ValidationResult(
                level="Schematron",
                findings=findings,
                duration_ms=int((time.time() - start_time) * 1000),
            )
        
        # Validate against Schematron rules
        try:
            is_valid = schematron.validate(xml_doc)
            
            if not is_valid:
                # Parse validation report
                report = schematron.validation_report
                if report is not None:
                    for error in report.iter():
                        if str(error.tag).endswith("failed-assert") or str(error.tag).endswith("successful-report"):
                            # Extract rule information
                            rule_id = error.get("id", "unknown")
                            test = error.get("test", "")
                            message = error.text.strip() if error.text else "Rule validation failed"
                            
                            # Determine severity based on rule type
                            level = FindingLevel.ERROR
                            if str(error.tag).endswith("successful-report"):
                                level = FindingLevel.WARNING
                            
                            findings.append(
                                Finding(
                                    level=level,
                                    code="SCHEMATRON:RULE_FAILURE",
                                    message=message,
                                    rule_ref=f"schematron://{rule_id}",
                                    location={
                                        "xpath": test,
                                        "rule_id": rule_id,
                                    },
                                )
                            )
            
        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="SCHEMATRON:VALIDATION_ERROR",
                    message=f"Schematron validation failed: {e}",
                    rule_ref="internal://Schematron",
                )
            )
    
    except Exception as e:
        findings.append(
            Finding(
                level=FindingLevel.ERROR,
                code="SCHEMATRON:VALIDATION_ERROR",
                message=f"Schematron validation failed: {e}",
                rule_ref="internal://Schematron",
            )
        )
    
    duration_ms = int((time.time() - start_time) * 1000)
    return ValidationResult(
        level="Schematron",
        findings=findings,
        duration_ms=duration_ms,
    )


def get_rules_info(rules_path: Path | None = None) -> dict[str, Any]:
    """
    Get information about the Schematron rules.
    
    Args:
        rules_path: Path to Schematron rules file
        
    Returns:
        Dictionary with rules information
    """
    if rules_path is None:
        rules_path = Path(__file__).parent.parent.parent.parent / "rules" / "schematron" / "5.0" / "business-rules.sch"
    
    info = {
        "rules_path": str(rules_path),
        "exists": rules_path.exists(),
        "title": None,
        "description": None,
        "patterns": [],
        "rules_count": 0,
    }
    
    if rules_path.exists():
        try:
            rules_doc = etree.parse(str(rules_path))
            root = rules_doc.getroot()
            
            # Extract title and description
            title_elem = root.find(".//{http://purl.oclc.org/dsdl/schematron}title")
            if title_elem is not None:
                info["title"] = title_elem.text
            
            desc_elem = root.find(".//{http://purl.oclc.org/dsdl/schematron}description")
            if desc_elem is not None:
                info["description"] = desc_elem.text
            
            # Extract patterns and rules
            patterns = root.findall(".//{http://purl.oclc.org/dsdl/schematron}pattern")
            for pattern in patterns:
                pattern_title = pattern.find("{http://purl.oclc.org/dsdl/schematron}title")
                pattern_info = {
                    "title": pattern_title.text if pattern_title is not None else "Untitled Pattern",
                    "rules": [],
                }
                
                rules = pattern.findall(".//{http://purl.oclc.org/dsdl/schematron}rule")
                for rule in rules:
                    rule_info = {
                        "context": rule.get("context", ""),
                        "assertions": [],
                    }
                    
                    assertions = rule.findall(".//{http://purl.oclc.org/dsdl/schematron}assert")
                    for assertion in assertions:
                        rule_info["assertions"].append({
                            "test": assertion.get("test", ""),
                            "message": assertion.text.strip() if assertion.text else "",
                        })
                    
                    pattern_info["rules"].append(rule_info)
                    info["rules_count"] += 1
                
                info["patterns"].append(pattern_info)
            
        except Exception as e:
            info["error"] = str(e)
    
    return info
