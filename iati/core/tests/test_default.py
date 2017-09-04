"""A module containing tests for the library representation of default values."""
import pytest
import iati.core.codelists
import iati.core.constants
import iati.core.default
import iati.core.schemas


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelist_valid_at_all_versions(self, standard_version_optional):
        """Check that a named default Codelist may be located.

        Todo:
            Check internal values beyond the codelists being the correct type.
        """
        name = 'Country'
        codelist = iati.core.default.codelist(name, *standard_version_optional)

        assert isinstance(codelist, iati.core.Codelist)
        assert codelist.name == name
        for code in codelist.codes:
            assert isinstance(code, iati.core.Code)

    @pytest.mark.parametrize("version, codelist_name, expected_type", [
        ('1.04', 'AidTypeFlag', iati.core.Codelist),
        ('1.05', 'AidTypeFlag', iati.core.Codelist),
        ('2.01', 'AidTypeFlag', ValueError),
        ('2.02', 'AidTypeFlag', ValueError),
        ('1.04', 'BudgetStatus', ValueError),
        ('1.05', 'BudgetStatus', ValueError),
        ('2.01', 'BudgetStatus', ValueError),
        ('2.02', 'BudgetStatus', iati.core.Codelist)
    ])
    def test_default_codelist_valid_only_at_some_versions(self, codelist_name, version, expected_type):
        """Check that a codelist that is valid at some version/s is not valid in other versions.
        For example:
            AidTypeFlag was an embedded codelist in v1.04 and v1.05, but is not valid at any version after this.
            For example, BudgetStatus was added as an embedded codelist in v2.02, so is not valid prior to this.
        """
        try:
            result = iati.core.default.codelist(codelist_name, version)
        except ValueError as excinfo:
            result = excinfo

        assert isinstance(result, expected_type)

    @pytest.mark.parametrize("name", iati.core.tests.utilities.generate_test_types(['str'], True))
    def test_default_codelist_invalid_at_all_versions(self, name, standard_version_optional):
        """Check that trying to find a default Codelist with an invalid name raises an error."""
        with pytest.raises(ValueError) as excinfo:
            iati.core.default.codelist(name, *standard_version_optional)

        assert 'There is no default Codelist in version' in str(excinfo.value)

    def test_default_codelists_type(self, standard_version_optional):
        """Check that the default Codelists are of the correct type.

        Todo:
            Check internal values beyond the codelists being the correct type.
        """
        codelists = iati.core.default.codelists(*standard_version_optional)

        assert isinstance(codelists, dict)
        for _, codelist in codelists.items():
            assert isinstance(codelist, iati.core.Codelist)

    def test_default_codelists_length(self, codelist_lengths_by_version):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        codelists = iati.core.default.codelists(codelist_lengths_by_version[0])

        assert len(codelists) == codelist_lengths_by_version[1]

    def test_default_activity_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.activity_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == len(iati.core.constants.STANDARD_VERSIONS)
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.ActivitySchema)

    def test_default_organisation_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.organisation_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == len(iati.core.constants.STANDARD_VERSIONS)
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.OrganisationSchema)

    def test_default_schemas(self):
        """Check that the default Schemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        version = iati.core.constants.STANDARD_VERSION_LATEST
        schemas = iati.core.default.schemas()

        assert isinstance(schemas, dict)
        assert isinstance(schemas[version], dict)
        assert len(schemas[version]) == 2
        for schema in schemas[version].values():
            assert isinstance(schema, (iati.core.ActivitySchema, iati.core.OrganisationSchema))

    @pytest.mark.parametrize("invalid_name", iati.core.tests.utilities.generate_test_types([], True))
    def test_default_schema(self, invalid_name):
        """Check that an Error is raised when attempting to load a Schema name that does not exist."""
        with pytest.raises((ValueError, TypeError)):
            iati.core.default.schema(invalid_name)
