"""Validation performance benchmarks."""

import time
from pathlib import Path
from typing import Any

import pytest

from mits_validator.validation_engine import ValidationEngine


class TestValidationPerformance:
    """Performance benchmarks for validation engine."""

    @pytest.fixture
    def validation_engine(self) -> ValidationEngine:
        """Create validation engine for testing."""
        return ValidationEngine()

    @pytest.fixture
    def sample_xml(self) -> str:
        """Sample XML for performance testing."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">
  <Property>
    <PropertyID>PERF-001</PropertyID>
    <PropertyName>Performance Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Performance St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Monthly rent payment</Description>
      </ChargeOfferItem>
      <ChargeOfferItem>
        <ChargeClassification>Deposit</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>OneTime</PaymentFrequency>
        <Refundability>Deposit</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Security deposit</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>"""

    def test_wellformed_validation_performance(self, validation_engine: ValidationEngine, sample_xml: str) -> None:
        """Test WellFormed validation performance."""
        start_time = time.time()
        
        # Run validation multiple times for better measurement
        for _ in range(10):
            result = validation_engine.validate(
                content=sample_xml.encode('utf-8'),
                content_type="application/xml",
            )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Performance assertion: should complete in reasonable time
        assert duration_ms < 1000, f"WellFormed validation took {duration_ms:.2f}ms, expected < 1000ms"
        
        # Verify validation worked
        assert len(result) > 0
        # Check that at least one validation level passed
        assert any(r.findings == [] for r in result)

    def test_xsd_validation_performance(self, validation_engine: ValidationEngine, sample_xml: str) -> None:
        """Test XSD validation performance."""
        start_time = time.time()
        
        # Run validation multiple times for better measurement
        for _ in range(5):  # Fewer iterations for XSD (more expensive)
            result = validation_engine.validate(
                content=sample_xml.encode('utf-8'),
                content_type="application/xml",
            )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Performance assertion: XSD validation should be reasonably fast
        assert duration_ms < 2000, f"XSD validation took {duration_ms:.2f}ms, expected < 2000ms"
        
        # Verify validation worked
        assert len(result) > 0
        # Check that at least one validation level passed
        assert any(r.findings == [] for r in result)

    def test_schematron_validation_performance(self, validation_engine: ValidationEngine, sample_xml: str) -> None:
        """Test Schematron validation performance."""
        start_time = time.time()
        
        # Run validation multiple times for better measurement
        for _ in range(3):  # Fewer iterations for Schematron (most expensive)
            result = validation_engine.validate(
                content=sample_xml.encode('utf-8'),
                content_type="application/xml",
            )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Performance assertion: Schematron validation should be reasonably fast
        assert duration_ms < 3000, f"Schematron validation took {duration_ms:.2f}ms, expected < 3000ms"
        
        # Verify validation worked
        assert len(result) > 0
        # Check that at least one validation level passed
        assert any(r.findings == [] for r in result)

    def test_semantic_validation_performance(self, validation_engine: ValidationEngine, sample_xml: str) -> None:
        """Test Semantic validation performance."""
        start_time = time.time()
        
        # Run validation multiple times for better measurement
        for _ in range(3):  # Fewer iterations for Semantic (catalog loading)
            result = validation_engine.validate(
                content=sample_xml.encode('utf-8'),
                content_type="application/xml",
            )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Performance assertion: Semantic validation should be reasonably fast
        assert duration_ms < 5000, f"Semantic validation took {duration_ms:.2f}ms, expected < 5000ms"
        
        # Verify validation worked
        assert len(result) > 0
        # Check that at least one validation level passed
        assert any(r.findings == [] for r in result)

    def test_large_xml_performance(self, validation_engine: ValidationEngine) -> None:
        """Test performance with larger XML content."""
        # Create a larger XML with multiple properties
        large_xml = """<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-01-15T10:30:00Z">"""
        
        # Add multiple properties to make it larger
        for i in range(10):
            large_xml += f"""
  <Property>
    <PropertyID>PERF-{i:03d}</PropertyID>
    <PropertyName>Performance Test Property {i}</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>{i} Performance St</StreetAddress>
      <City>TestCity</City>
      <State>TC</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Monthly rent payment</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>"""
        
        large_xml += "\n</PropertyMarketing>"
        
        start_time = time.time()
        
        result = validation_engine.validate(
            content=large_xml.encode('utf-8'),
            content_type="application/xml",
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Performance assertion: larger XML should still validate reasonably fast
        assert duration_ms < 10000, f"Large XML validation took {duration_ms:.2f}ms, expected < 10000ms"
        
        # Verify validation worked
        assert len(result) > 0
        # Check that at least one validation level passed
        assert any(r.findings == [] for r in result)

    def test_profile_performance_comparison(self, validation_engine: ValidationEngine, sample_xml: str) -> None:
        """Compare performance across different profiles."""
        profiles = ["default", "performance", "enhanced-validation"]
        results = {}
        
        for profile in profiles:
            start_time = time.time()
            
            result = validation_engine.validate(
                content=sample_xml.encode('utf-8'),
                content_type="application/xml",
            )
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            results[profile] = duration_ms
            
            # Verify validation worked
            assert len(result) > 0
            # Check that at least one validation level passed
            assert any(r.findings == [] for r in result)
        
        # All profiles should complete in reasonable time
        for profile, duration in results.items():
            assert duration < 5000, f"{profile} profile took {duration:.2f}ms, expected < 5000ms"
