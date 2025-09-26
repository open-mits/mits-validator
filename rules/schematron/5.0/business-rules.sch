<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">

  <sch:pattern>
    <sch:rule context="*">
      <sch:assert test="not(local-name()='ChargeClassification' and . != 'Rent' and . != 'Deposit' and . != 'Pet' and . != 'Parking' and . != 'Utilities' and . != 'Technology' and . != 'Admin' and . != 'OtherMandatory')">
        Charge classification is not valid
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*">
      <sch:assert test="not(local-name()='Requirement' and . = 'Mandatory' and not(../*[local-name()='PaymentFrequency']))">
        Mandatory charges must have a PaymentFrequency specified
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*">
      <sch:assert test="not(local-name()='Refundability' and . = 'Deposit' and not(../*[local-name()='Description']) and not(../*[local-name()='Amount']))">
        Deposit charges must have either a Description or Amount specified
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:rule context="*">
      <sch:assert test="not(local-name()='PropertyID' and string-length(.) = 0)">
        Property must have a non-empty PropertyID
      </sch:assert>
      <sch:assert test="not(local-name()='PropertyName' and string-length(.) = 0)">
        Property must have a non-empty PropertyName
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>