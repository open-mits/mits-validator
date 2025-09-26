<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
  <title>MITS Property Validation Rules</title>
  <ns prefix="mits" uri="http://www.mits.org/schema"/>
  
  <pattern id="property-id-required">
    <title>Property ID is required</title>
    <rule context="mits:Property">
      <assert test="mits:ID and string-length(mits:ID) > 0">
        Property must have a non-empty ID
      </assert>
    </rule>
  </pattern>
  
  <pattern id="price-positive">
    <title>Price must be positive</title>
    <rule context="mits:Property[mits:Price]">
      <assert test="number(mits:Price) > 0">
        Property price must be greater than zero
      </assert>
    </rule>
  </pattern>
  
  <pattern id="address-complete">
    <title>Address must be complete</title>
    <rule context="mits:Property/mits:Address">
      <assert test="mits:Street and mits:City and mits:State and mits:ZipCode">
        Property address must include Street, City, State, and ZipCode
      </assert>
    </rule>
  </pattern>
  
  <pattern id="provider-name-required">
    <title>Provider name is required</title>
    <rule context="mits:Header/mits:Provider">
      <assert test="mits:Name and string-length(mits:Name) > 0">
        Provider must have a non-empty Name
      </assert>
    </rule>
  </pattern>
</schema>
