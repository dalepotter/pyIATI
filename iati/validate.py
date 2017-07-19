"""A module containing validation functionality.

Warning:
    It is planned to change from Schema-based to Data-based Codelist validation. As such, this module will change significantly.
"""

from lxml import etree
import iati.core.default


def _correct_codes(dataset, codelist):
    """Determine whether a given Dataset has values from the specified Codelist where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        codelist_name (str): The name of the Codelist to check values from.

    Returns:
        bool: A boolean indicating whether the given Dataset has values from the specified Codelist where they should be.

    Todo:
        Test invalid Codelist name.
        Test something with a condition.

    """
    mappings = iati.core.default.codelist_mapping()
    codes_to_check = []

    for mapping in mappings[codelist.name]:
        base_xpath = mapping['xpath']
        condition = mapping['condition']
        if condition is None:
            xpath = base_xpath
        else:
            # insert condition into the xpath
            split_xpath = base_xpath.split('/')
            parent_el_xpath = '/'.join(split_xpath[:-1])
            attr_xpath = split_xpath[-1:][0]
            xpath = parent_el_xpath + '[' + condition + ']/' + attr_xpath
        codes_to_check = codes_to_check + dataset.xml_tree.xpath(xpath)

    for code in codes_to_check:
        if code not in codelist.codes:
            return False

    return True


def _correct_codelist_values(dataset, schema):
    """Determine whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.core.schemas.Schema): The Schema to locate Codelists within.

    Returns:
        bool: A boolean indicating whether the given Dataset has values from the specified Codelists where they should be.

    """
    for codelist in schema.codelists:
        correct_for_codelist = _correct_codes(dataset, codelist)
        if not correct_for_codelist:
            return False

    return True


def _correct_rule_conformance(dataset, ruleset):
    """Determine whether a given Dataset conforms to the Rules in a Ruleset.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Rule conformance with.
        ruleset (iati.core.rulesets.Ruleset): The Ruleset to check Rules within.

    Returns:
        bool: A boolean indicating whether the given Dataset conforms to all the Rules in the given Ruleset.

    Todo:
    	Determine a better name for this function.

    """
    for rule in ruleset.rules:
    	if not rule.is_valid_for(dataset):
    		return False

    return True


def _correct_ruleset_conformance(dataset, schema):
    """Determine whether a given Dataset conforms to the Rulesets that have been added to a Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Rule conformance with.
        schema (iati.core.schemas.Schema): The Schema to locate Rulesets within.

    Returns:
        bool: A boolean indicating whether the given Dataset conforms to the required Rulesets.

    Todo:
    	Determine a better name for this function.

    """
    for ruleset in schema.rulesets:
        conforms_with_ruleset = _correct_rule_conformance(dataset, ruleset)
        if not conforms_with_ruleset:
            return False

    return True


def is_iati_xml(dataset, schema):
    """Determine whether a given Dataset's XML is valid against the specified Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML against the given Schema.

    Raises:
        iati.core.exceptions.SchemaError: An error occurred in the parsing of the Schema.

    Todo:
        Create test against a bad Schema.

    """
    try:
        validator = schema.validator()
    except iati.core.exceptions.SchemaError as err:
        raise err

    try:
        validator.assertValid(dataset.xml_tree)
    except etree.DocumentInvalid:
        return False

    return True


def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.core.Dataset): The Dataset to check validity of.
        schema (iati.core.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid against the given Schema.

    Todo:
        Create test against a bad Schema.

    """
    try:
        iati_xml = is_iati_xml(dataset, schema)
        if not iati_xml:
            return False
    except iati.core.exceptions.SchemaError:
        return False

    return _correct_codelist_values(dataset, schema) and _correct_ruleset_conformance(dataset, schema)


def is_xml(maybe_xml):
    """Determine whether a given parameter is XML.


    Args:
        maybe_xml (str): An string that may or may not contain valid XML.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML.

    """
    if isinstance(maybe_xml, iati.core.data.Dataset):
        maybe_xml = maybe_xml.xml_str

    try:
        _ = etree.fromstring(maybe_xml.strip())
        return True
    except (etree.XMLSyntaxError, AttributeError, TypeError, ValueError):
        return False
