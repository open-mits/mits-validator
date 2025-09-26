<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">

  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeClassification']">
      <sch:assert test=". = 'Rent' or . = 'Deposit' or . = 'Pet' or . = 'Parking' or . = 'Utilities' or . = 'Technology' or . = 'Admin' or . = 'OtherMandatory'">
        Charge classification is not valid
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']">
      <sch:assert test="not(*[local-name()='Requirement'] = 'Mandatory' and not(*[local-name()='PaymentFrequency']))">
        Mandatory charges must have a PaymentFrequency specified
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']">
      <sch:assert test="not(*[local-name()='Refundability'] = 'Deposit' and not(*[local-name()='Description']) and not(*[local-name()='Amount']))">
        Deposit charges must have either a Description or Amount specified
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*[local-name()='Property']">
      <sch:assert test="*[local-name()='PropertyID'] and string-length(*[local-name()='PropertyID']) &gt; 0">
        Property must have a non-empty PropertyID
      </sch:assert>
      <sch:assert test="*[local-name()='PropertyName'] and string-length(*[local-name()='PropertyName']) &gt; 0">
        Property must have a non-empty PropertyName
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Amount validation rules -->
  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']">
      <sch:assert test="not(*[local-name()='Amount'] and *[local-name()='Amount'] &lt; 0)">
        Charge amounts cannot be negative
      </sch:assert>
      <sch:assert test="not(*[local-name()='Amount'] and *[local-name()='Amount'] = '')">
        Charge amounts must be numeric values
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Payment frequency validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='PaymentFrequency']">
      <sch:assert test=". = 'OneTime' or . = 'Monthly' or . = 'Weekly' or . = 'Daily' or . = 'PerUse' or . = 'PerEvent'">
        Payment frequency must be a valid value (OneTime, Monthly, Weekly, Daily, PerUse, PerEvent)
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Refundability validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='Refundability']">
      <sch:assert test=". = 'Refundable' or . = 'NonRefundable' or . = 'Deposit' or . = 'Conditional'">
        Refundability must be a valid value (Refundable, NonRefundable, Deposit, Conditional)
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Term basis validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='TermBasis']">
      <sch:assert test=". = 'LeaseTerm' or . = 'Rolling' or . = 'Fixed' or . = 'PerEvent'">
        Term basis must be a valid value (LeaseTerm, Rolling, Fixed, PerEvent)
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Address completeness validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='Address']">
      <sch:assert test="*[local-name()='StreetAddress'] and string-length(*[local-name()='StreetAddress']) &gt; 0">
        Address must have a non-empty StreetAddress
      </sch:assert>
      <sch:assert test="*[local-name()='City'] and string-length(*[local-name()='City']) &gt; 0">
        Address must have a non-empty City
      </sch:assert>
      <sch:assert test="*[local-name()='State'] and string-length(*[local-name()='State']) &gt; 0">
        Address must have a non-empty State
      </sch:assert>
      <sch:assert test="*[local-name()='PostalCode'] and string-length(*[local-name()='PostalCode']) &gt; 0">
        Address must have a non-empty PostalCode
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Property type validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='PropertyType']">
      <sch:assert test=". = 'Apartment' or . = 'House' or . = 'Townhouse' or . = 'Condo' or . = 'Studio' or . = 'Loft' or . = 'Duplex' or . = 'Other'">
        Property type must be a valid value (Apartment, House, Townhouse, Condo, Studio, Loft, Duplex, Other)
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Charge consistency validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']">
      <sch:assert test="not(*[local-name()='Requirement'] = 'Optional' and *[local-name()='PaymentFrequency'] = 'OneTime' and not(*[local-name()='Amount']))">
        Optional OneTime charges should specify an Amount
      </sch:assert>
      <sch:assert test="not(*[local-name()='Refundability'] = 'Deposit' and *[local-name()='Requirement'] = 'Optional')">
        Deposit charges should typically be Mandatory, not Optional
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Business logic validation -->
  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']">
      <sch:assert test="not(*[local-name()='ChargeClassification'] = 'Rent' and *[local-name()='Requirement'] = 'Optional')">
        Rent charges should typically be Mandatory, not Optional
      </sch:assert>
      <sch:assert test="not(*[local-name()='ChargeClassification'] = 'Deposit' and *[local-name()='PaymentFrequency'] != 'OneTime')">
        Deposit charges should typically be OneTime payments
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>