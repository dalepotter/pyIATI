"""A module containing tests for the library representation of Rulesets."""
import pytest
import lxml
import iati.core.default
import iati.core.rulesets
import iati.core.resources
import iati.core.tests.utilities


class TestRuleset(object):
    """A container for tests relating to Rulesets."""

    def test_ruleset_init_no_parameters(self):
        """Check that a Ruleset cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            iati.core.Ruleset()

    def test_ruleset_init_ruleset_str_valid(self):
        """Check that a Ruleset is created when given a JSON Ruleset in string format."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": []}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert ruleset.rules == set()

    @pytest.mark.parametrize("not_a_ruleset", iati.core.tests.utilities.find_parameter_by_type(['str', 'bytearray'], False))
    def test_ruleset_init_ruleset_str_not_str(self, not_a_ruleset):
        """Check that a Ruleset cannot be created when given at least one Rule in a non-string format."""
        with pytest.raises(ValueError):
            iati.core.Ruleset(not_a_ruleset)

    @pytest.mark.parametrize("byte_array", iati.core.tests.utilities.find_parameter_by_type(['bytearray']))
    def test_ruleset_init_ruleset_str_bytearray(self, byte_array):
        """Check that a Ruleset cannot be created when given at least one Rule in a bytearray format."""
        with pytest.raises(ValueError):
            iati.core.Ruleset(byte_array)

    def test_ruleset_init_ruleset_str_invalid(self):
        """Check that a Ruleset cannot be created when given a string that is not a Ruleset."""
        not_a_ruleset_str = 'This is not a ruleset: It is a cat. Meow, meow.'

        with pytest.raises(ValueError):
            iati.core.Ruleset(not_a_ruleset_str)

    def test_ruleset_init_ruleset_1_rule(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with one Rule."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 1
        assert isinstance(list(ruleset.rules)[0], iati.core.Rule)
        assert isinstance(list(ruleset.rules)[0], iati.core.RuleAtLeastOne)

    def test_ruleset_init_ruleset_1_rule_invalid_type(self):
        """Check that a Ruleset raises a KeyError when given a JSON Ruleset in string format with an invalid rule_type key."""
        ruleset_str = '{"CONTEXT": {"invalid_rule_type": {"cases": [{"paths": ["test_path"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_2_rules_single_case(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules under a single case."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}, {"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
            assert isinstance(rule, iati.core.RuleAtLeastOne)

    def test_ruleset_init_ruleset_multiple_cases(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of different types, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.RuleAtLeastOne)]) == 1
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.RuleNoMoreThanOne)]) == 1

    def test_ruleset_init_ruleset_duplicate_types(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_duplicate_contexts(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"DUPLICATE_CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "DUPLICATE_CONTEXT": {"no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_multiple_contexts(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of the same type, each under a different context."""
        ruleset_str = '{"CONTEXT_1": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "CONTEXT_2": {"atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
            assert isinstance(rule, iati.core.RuleAtLeastOne)


class TestRule(object):
    """A container for tests relating to Rules."""

    def test_rule_class_cannot_be_instantiated_directly_without_name(self):
        """Check that Rule itself cannot be directly instantiated."""
        xpath_base = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(AttributeError):
            iati.core.Rule(xpath_base, case)

    def test_rule_class_cannot_be_instantiated_directly_with_name(self):
        """Check that Rule itself cannot be directly instantiated with a Rule name."""
        name = 'atleast_one'
        xpath_base = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(TypeError):
            iati.core.Rule(name, xpath_base, case)


class TestRuleSubclasses(object):
    """A container for tests relating to all Rule subclasses."""

    @pytest.fixture(params=[
        iati.core.rulesets.locate_constructor_for_rule_type(rule_type) for rule_type in iati.core.rulesets._VALID_RULE_TYPES
    ])
    def rule_constructor(self, request):
        """Return constructor for the current type of Rule.

        Note:
            Differs from fixture of same name in RuleSubclassTestBase as specifies rule_type by _VALID_RULE_TYPES rather than via specific TestRuleSubclass.

        """
        return request.param

    def test_rule_init_no_parameters(self, rule_constructor):
        """Check that a Rule cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            rule_constructor()

    @pytest.mark.parametrize("case", iati.core.tests.utilities.find_parameter_by_type(['mapping'], False))
    def test_rule_init_invalid_case(self, rule_constructor, case):
        """Check that a Rule cannot be created when case is not a dictionary."""
        xpath_base = 'an xpath'

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, case)

    def test_rule_init_invalid_case_property(self, rule_constructor):
        """Check that a Rule cannot be created when a case has a property that is not permitted."""
        xpath_base = 'an xpath'
        case = {'thisis_an_invalidkey': ['this_is_a_value']}

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, case)


class RuleSubclassTestBase(object):
    """A base class for Rule subclass tests."""

    @pytest.fixture
    def xpath_base(self):
        """Return valid xpath_base."""
        return '//root_element'

    @pytest.fixture
    def empty_xpath_base(self):
        """Empty_xpath_base."""
        return ''

    @pytest.fixture
    def rule_basic_init(self, rule_constructor, valid_case, xpath_base):
        """Rule subclass."""
        return rule_constructor(xpath_base, valid_case)

    # @pytest.fixture
    # def rule_is_valid_for_case(self, rule_constructor, xpath_base, case_for_is_valid_for):
    #     """Rule with specific cases for checking the `is_valid_for` function."""
    #     return rule_constructor(xpath_base, case_for_is_valid_for)

    @pytest.fixture
    def rule_empty_xpath_base(self, rule_constructor, valid_case, empty_xpath_base):
        """Rule subclass with an empty xpath_base."""
        return rule_constructor(empty_xpath_base, valid_case)

    @pytest.fixture
    def rule_valid_empty_case(self, empty_path_case, xpath_base, rule_constructor):
        """Rule with a valid empty path case."""
        return rule_constructor(xpath_base, empty_path_case)

    @pytest.fixture
    def rule_empty_xpath_base_and_paths(self, rule_constructor, empty_xpath_base, empty_path_case):
        """Rule subclass with an empty xpath_base and empty path case."""
        return rule_constructor(empty_xpath_base, empty_path_case)

    @pytest.fixture
    def rule_constructor(self, rule_type):
        """Return current Rule type.

        Note:
            Differs from fixture of same name in TestRuleSubclass as specifies rule_type via specific TestRuleSubclass fixture.

        """
        return iati.core.rulesets.locate_constructor_for_rule_type(rule_type)

    def test_rule_init_valid_parameter_types(self, rule_basic_init):
        """Check that Rule subclasses can be instantiated with valid parameter types."""
        assert isinstance(rule_basic_init, iati.core.Rule)

    def test_rule_init_valid_empty_path_case(self, rule_valid_empty_case):
        """Check that Rule subclasses can be instantiated with a valid empty case parameter."""
        assert isinstance(rule_valid_empty_case, iati.core.Rule)

    def test_rule_attributes_from_case(self, rule_basic_init):
        """Check that a Rule subclass has case attributes set."""
        required_attributes = rule_basic_init._required_case_attributes(rule_basic_init._ruleset_schema_section())
        for attrib in required_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(rule_basic_init, attrib)

    def test_rule_name(self, rule_basic_init, rule_type):
        """Check that a Rule subclass has the expected name."""
        assert rule_basic_init.name == rule_type

    def test_rule_paths(self, rule_basic_init):
        """Check that a Rule subclass has the expected paths."""
        # Exclude rules with no `paths` attribute.
        if 'paths' in dir(rule_basic_init):
            for path in rule_basic_init.paths:
                assert path.startswith(rule_basic_init.xpath_base)

    @pytest.mark.parametrize("xpath_base", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_rule_init_invalid_xpath_base(self, rule_constructor, xpath_base, valid_case):
        """Check that a Rule subclass cannot be created when xpath_base is not a string."""
        with pytest.raises(TypeError):
            rule_constructor(xpath_base, valid_case)

    def test_rule_invalid_case(self, rule_constructor, invalid_case):
        """Check that a Rule cannot be instantiated when the case is invalid."""
        xpath_base = 'an xpath'

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, invalid_case)

    def test_is_valid_for(self, valid_dataset, rule_basic_init):
        """Check that a given Rule returns the expected result when given Dataset."""
        # import pdb; pdb.set_trace()
        assert rule_basic_init.is_valid_for(valid_dataset)

    # def test_is_invalid_for(self, invalid_dataset, rule_is_valid_for_case):
    #     """Check that a given Rule returns the expected result when given a Dataset."""
    #     assert not rule_is_valid_for_case.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_data", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_is_valid_for_raises_error_on_non_permitted_argument(self, rule_basic_init, junk_data):
        """Check that a given Rule returns expected error when passed an argument that is not a Dataset."""
        with pytest.raises(AttributeError):
            rule_basic_init.is_valid_for(junk_data)

    def test_is_valid_for_raises_error_when_passed_an_etree(self, rule_basic_init):
        """Check that an error is raised if an etree is given as an argument instead of a Dataset.

        Todo:
            Use more generic Dataset.

        """
        with pytest.raises(AttributeError):
            rule_basic_init.is_valid_for(iati.core.resources.load_as_tree(iati.core.resources.get_test_data_path('valid_atleastone')))

    def test_empty_xpath_base_rule_init_normalised_paths(self, rule_empty_xpath_base):
        """Check that a Rule with an empty xpath_base can be instantiated correctly with normalised `paths`.

        Note:
            Rules without `paths` are checked for correct normalisation in their own TestRuleSubclass.

        """
        if 'paths' in dir(rule_empty_xpath_base):
            for path in rule_empty_xpath_base.paths:
                assert path.startswith(rule_empty_xpath_base.xpath_base)

    def test_empty_xpath_base_empty_path_is_valid_for(self, rule_empty_xpath_base_and_paths, valid_dataset):
        """Check that a Rule with an empty xpath_base and empty paths raises error."""
        # RuleStartswith raises an IndexError instead.
        with pytest.raises((lxml.etree.XPathEvalError, IndexError)):
            rule_empty_xpath_base_and_paths.is_valid_for(valid_dataset)


class TestRuleAtLeastOne(RuleSubclassTestBase):
    """A container for tests relating to RuleAtLeastOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'atleast_one'

    @pytest.fixture(params=[
        {'paths': ['element1']},  # single path
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element5/@attribute']},  # single path for attribute
        {'paths': ['element6/@attribute', 'element7/@attribute']},  # multiple paths for attribute
        {'paths': ['element8/@attribute', 'element8/@attribute']}  # duplicate paths for attribute
    ])
    def valid_case(self, request):
        """Permitted case for this Rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': []},  # empty path array
        {'paths': 'element'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['element', 3]},  # mixed string and non-string value in path array
        {},  # empty dictionary
        {'paths': {'element'}},  # dictionary paths
        {'paths': 'element'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['element/@attribute', 3]},  # mixed string and non-string value in path array
        {},  # empty dictionary
        {'paths': {'element/@attribute'}}  # dictionary paths
    ])
    def invalid_case(self, request):
        """Non-permitted case for this Rule."""
        return request.param

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_VALID

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_INVALID

    @pytest.fixture
    def empty_path_case(self):
        """Empty path string for RuleAtLeastOne."""
        return {'paths': ['']}

#
# class TestRuleDateOrder(RuleSubclassTestBase):
#     """A container for tests relating to RuleDateOrder.
#
#     Todo:
#         Are equal dates actually accounted for in the definition of this Rule?
#         Reimplement 'NOW' as current implementation incorrect.
#         Test implementation of functionality to ignore function call if `less` or `more` do not return dates.
#
#     """
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'date_order'
#
#     @pytest.fixture(params=[
#         # {'less': '', 'more': ''},  # `less` and `more` empty strings
#         {'less': 'element1', 'more': 'element2'},  # both `less` and `more` present
#         # {'less': 'start-xpath', 'more': 'NOW'},  # `more` as NOW
#         # {'less': 'NOW', 'more': 'end-xpath'},  # `less` as NOW
#         # {'less': 'NOW', 'more': 'NOW'},  # both `less` and `more` as NOW
#         {'less': 'element3', 'more': 'element3'},  # both `less` and `more` duplicate xpath
#         # {'less': '', 'more': 'element4'},  # `less` is an empty string
#         # {'less': 'element5', 'more': ''},  # `more` is an empty string
#         {'less': 'element4/@attribute', 'more': 'element4/@attribute'},  # both `less` and `more` present
#         # {'less': 'start-xpath/@attribute', 'more': 'NOW'},  # `more` as NOW
#         # {'less': 'NOW', 'more': 'end-xpath/@attribute'},  # `less` as NOW
#         {'less': 'element5/@attribute', 'more': 'element5/@attribute'},  # both `less` and `more` duplicate xpath
#         # {'less': '', 'more': 'end-xpath/@attribute'},  # `less` is a string-formatted date
#         # {'less': 'start-xpath/@attribute', 'more': ''}  # `more` is a string-formatted date
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'less': 'start'},  # missing required attribute - `more`
#         {'more': 'end'},  # missing required attribute - `less`
#         {'less': 1501075031590, 'more': 'end-xpath'},  # `less` is not a string
#         {'less': 'start-xpath', 'more': 1501075031590},  # `more` is not a string
#         {},  # empty dictionary
#         {'less': ['start']},  # less is a list
#         {'more': ['end']}  # more is a list
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_VALID
#
#     # @pytest.fixture(params=[
#     #     {'less': 'planned-disbursement/period-start/@iso-date', 'more': 'planned-disbursement/period-end/@iso-date'}
#     # ])
#     # def case_for_is_valid_for(self, request):
#     #     """Case to check the `is_valid_for` function of RuleDateOrder."""
#     #     return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty strings for RuleDateOrder."""
#         return {'less': '', 'more': ''}
#
#     def test_rule_paths_less(self, rule_basic_init):
#         """Check that the `less` value has been combined with the `xpath_base` where required."""
#         if rule_basic_init.less.endswith(rule_basic_init.special_case):
#             assert rule_basic_init.less == rule_basic_init.special_case
#         else:
#             assert rule_basic_init.less.startswith(rule_basic_init.xpath_base)
#
#     def test_rule_paths_more(self, rule_basic_init):
#         """Check that the `more` value has been combined with the `xpath_base` where required."""
#         if rule_basic_init.more.endswith(rule_basic_init.special_case):
#             assert rule_basic_init.more == rule_basic_init.special_case
#         else:
#             assert rule_basic_init.more.startswith(rule_basic_init.xpath_base)
#
#     # def test_incorrect_date_format_raises_error(self, rule_is_valid_for_case):
#     #     """Check that a dataset with dates in an incorrect format raise expected error."""
#     #     with pytest.raises(ValueError):
#     #         rule_is_valid_for_case.is_valid_for(iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_INVALID_DATE_FORMAT)
#
#
# class TestRuleDependent(RuleSubclassTestBase):
#     """A container for tests relating to RuleDependent."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'dependent'
#
#     @pytest.fixture(params=[
#         {'paths': ['path_1']},  # single path
#         {'paths': ['path_1', 'path_2']},  # multiple paths
#         {'paths': ['path_1', 'path_1']}  # duplicate paths
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'paths': []},  # empty path array
#         {'paths': 'path_1'},  # non-array `paths`
#         {'paths': [3]},  # non-string value in path array
#         {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {},  # empty dictionary
#         {'paths': {'path_1'}}  # path value is dictionary instead of list
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_VALID
#
#     @pytest.fixture(params=[
#         {"paths": ["transaction/provider-org", "location/point"]}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleDependent."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleDependent."""
#         return {'paths': ['']}
#
#
# class TestRuleNoMoreThanOne(RuleSubclassTestBase):
#     """A container for tests relating to RuleNoMoreThanOne."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'no_more_than_one'
#
#     @pytest.fixture(params=[
#         {'paths': ['path_1']},  # single path
#         {'paths': ['path_1', 'path_2']},  # multiple paths
#         {'paths': ['path_1', 'path_1']}  # duplicate paths
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'paths': []},  # empty path array
#         {'paths': 'path_1'},  # non-array `paths`
#         {'paths': [3]},  # non-string value in path array
#         {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {},  # empty dictionary
#         {'paths': {'path_1'}}  # dictionary paths
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'paths': ['element_that_only_occurs_once']},
#         {'paths': ['element_that_only_occurs_once', 'another_element_that_only_occurs_once']}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleNoMoreThanOne."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleNoMoreThanOne."""
#         return {'paths': ['']}
#
#
# class TestRuleRegexMatches(RuleSubclassTestBase):
#     """A container for tests relating to RuleRegexMatches."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'regex_matches'
#
#     @pytest.fixture(params=[
#         {'regex': 'some regex', 'paths': ['path_1']},  # single path with regex
#         {'regex': 'some regex', 'paths': ['path_1', 'path_2']},  # multiple paths with regex
#         {'regex': 'some regex', 'paths': ['path_1', 'path_1']},  # duplicate paths with regex
#         {'regex': '', 'paths': ['path_1']}  # single path with regex
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'regex': 'some regex', 'paths': []},  # empty path array
#         {'regex': 'some regex', 'paths': 'path_1'},  # non-array `paths`
#         {'regex': 'some regex', 'paths': [3]},  # non-string value in path array
#         {'regex': 'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {'regex': 'some regex'},  # missing required attribute - `paths`
#         {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
#         {'regex': '[', 'paths': ['path_1']},  # provided string not a valid regex
#         {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
#         {},  # empty dictionary
#         {'regex': 'some regex', 'paths': {'path_1'}},  # dictionary paths
#         {'regex': ['some regex'], 'paths': 'path_1'}  # list regex
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'regex': r"[^\/\\&\\|\\?]+", 'paths': ['iati-identifier']}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleRegexMatches."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleRegexMatches."""
#         return {'regex': r'[^\/\\&\\|\\?]+', 'paths': ['']}
#
#
# class TestRuleRegexNoMatches(RuleSubclassTestBase):
#     """A container for tests relating to RuleRegexNoMatches."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'regex_no_matches'
#
#     @pytest.fixture(params=[
#         {'regex': 'some regex', 'paths': ['path_1']},  # single path with regex
#         {'regex': 'some regex', 'paths': ['path_1', 'path_2']},  # multiple paths with regex
#         {'regex': 'some regex', 'paths': ['path_1', 'path_1']},  # duplicate paths with regex
#         {'regex': '', 'paths': ['path_1']}  # single path with regex
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'regex': 'some regex', 'paths': []},  # empty path array
#         {'regex': 'some regex', 'paths': 'path_1'},  # non-array `paths`
#         {'regex': 'some regex', 'paths': [3]},  # non-string value in path array
#         {'regex': 'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {'regex': 'some regex'},  # missing required attribute - `paths`
#         {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
#         {'regex': '[', 'paths': ['path_1']},  # provided string not a valid regex
#         {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
#         {},  # empty dictionary
#         {'regex': 'some regex', 'paths': {'path_1'}},  # dictionary paths
#         {'regex': ['some regex'], 'paths': 'path_1'}  # list regex
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'regex': r'[^\/\\&\\|\\?]+', 'paths': ['iati-identifier']}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleRegexNoMatches."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleRegexNoMatches."""
#         return {'regex': r'[^\/\\&\\|\\?]+', 'paths': ['']}
#
#
# class TestRuleStartsWith(RuleSubclassTestBase):
#     """A container for tests relating to RuleStartsWith."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'startswith'
#
#     @pytest.fixture(params=[
#         {'start': 'prefix-xpath', 'paths': ['path_1']},  # single path with prefix
#         {'start': 'prefix-xpath', 'paths': ['path_1', 'path_2']},  # multiple paths with prefix
#         {'start': 'prefix-xpath', 'paths': ['path_1', 'path_1']},  # duplicate paths with prefix
#         {'start': '', 'paths': ['path_1']}  # single path with prefix
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'start': 'prefix-xpath', 'paths': []},  # empty path array
#         {'start': 'prefix-xpath', 'paths': 'path_1'},  # non-array `paths`
#         {'start': 'prefix-xpath', 'paths': [3]},  # non-string value in path array
#         {'start': 'prefix-xpath', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {'start': 3, 'paths': ['path_1']},  # provided prefix xpath not a string
#         {'start': 'prefix-xpath'},  # missing required attribute - `paths`
#         {'paths': ['path_1', 'path_2']},  # missing required attribute - `start`
#         {},  # empty dictionary
#         {'start': 'prefix-xpath', 'paths': {'path_1'}},  # dictionary paths
#         {'start': ['prefix-xpath'], 'paths': ['path_1']}  # list start
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'start': 'reporting-org/@ref', 'paths': ['iati-identifier']}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleStartsWith."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleStartsWith."""
#         return {'start': 'reporting-org/@ref', 'paths': ['']}
#
#     def test_rule_paths_start(self, rule_basic_init):
#         """Check that the `start` value has been combined with the `xpath_base`."""
#         assert rule_basic_init.start.startswith(rule_basic_init.xpath_base)
#
#
# class TestRuleSum(RuleSubclassTestBase):
#     """A container for tests relating to RuleSum."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'sum'
#
#     @pytest.fixture(params=[
#         {'paths': ['path_1'], 'sum': 3},  # single path with sum
#         {'paths': ['path_1', 'path_2'], 'sum': 3},  # multiple paths with sum
#         {'paths': ['path_1', 'path_1'], 'sum': 3},  # duplicate paths with sum
#         {'paths': ['path_1'], 'sum': -1000},  # negative sum
#         {'paths': ['path_1'], 'sum': 101},  # sum greater than standard percentage limit
#         {'paths': ['path_1'], 'sum': 15.5},  # decimal sum
#         {'paths': ['path_1'], 'sum': 0},  # zero sum
#         {'paths': ['path_1'], 'sum': 10**100},  # big sum
#         {'paths': ['path_1'], 'sum': -10**100},  # tiny sum
#         {'paths': ['path_1'], 'sum': 2.99792458e6}  # exponential sum
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'paths': [], 'sum': 3},  # empty path array
#         {'paths': 'path_1', 'sum': 3},  # non-array `paths`
#         {'paths': [3], 'sum': 3},  # non-string value in path array
#         {'paths': ['path_1', 3], 'sum': 3},  # mixed string and non-string value in path array
#         {'paths': ['path_1', 'path_2']},  # missing required attribute - `sum`
#         {'sum': 100},  # missing required attribute - `paths`
#         {},  # empty dictionary
#         {'paths': ['path_1'], 'sum': '3'},  # sum is a string representation of a number
#         {'sum': 100, 'paths': {'path_1'}},  # dictionary paths
#         {'sum': [100], 'paths': 'path_1'}  # list sum
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'paths': ['recipient-country/@percentage', 'recipient-region/@percentage'], 'sum': 100}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleSum."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleSum."""
#         return {'paths': [''], 'sum': 100}
#
#
# class TestRuleUnique(RuleSubclassTestBase):
#     """A container for tests relating to RuleUnique."""
#
#     @pytest.fixture
#     def rule_type(self):
#         """Type of Rule."""
#         return 'unique'
#
#     @pytest.fixture(params=[
#         {'paths': ['path_1']},  # single path
#         {'paths': ['path_1', 'path_2']},  # multiple paths
#         {'paths': ['path_1', 'path_1']}  # duplicate paths
#     ])
#     def valid_case(self, request):
#         """Permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture(params=[
#         {'paths': []},  # empty path array
#         {'paths': 'path_1'},  # non-array `paths`
#         {'paths': [3]},  # non-string value in path array
#         {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
#         {},  # empty dictionary
#         {'paths': {'path_1'}}
#     ])
#     def invalid_case(self, request):
#         """Non-permitted case for this Rule."""
#         return request.param
#
#     @pytest.fixture
#     def invalid_dataset(self):
#         """Invalid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_INVALID
#
#     @pytest.fixture
#     def valid_dataset(self):
#         """Return valid dataset for this Rule."""
#         return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_VALID
#
#     @pytest.fixture(params=[
#         {'paths': ['iati-identifier']},
#         {'paths': ['iati-identifier', 'other_unique_element']}
#     ])
#     def case_for_is_valid_for(self, request):
#         """Case to check the `is_valid_for` function of RuleUnique."""
#         return request.param
#
#     @pytest.fixture
#     def empty_path_case(self):
#         """Empty path string for RuleUnique."""
#         return {'paths': ['']}
