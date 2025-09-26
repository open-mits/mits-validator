<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">

  <sch:pattern>
    <sch:rule context="*[local-name()='ChargeOfferItem']/*[local-name()='ChargeClassification']">
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

</sch:schema>