INTERACTIVE_TAGS = [
    'a', 'button', 'details', 'embed', 'input', 'label','option',
    'menu', 'menuitem', 'object', 'select', 'textarea', 'summary'
]

INTERACTIVE_ROLES = [
    'button', 'menu', 'menuitem', 'link', 'checkbox', 'radio',
    'slider', 'tab', 'tabpanel', 'textbox', 'combobox', 'grid',
    'listbox', 'option', 'progressbar', 'scrollbar', 'searchbox','presentation',
    'switch', 'tree', 'treeitem', 'spinbutton', 'tooltip', 'a-button-inner', 'a-dropdown-button', 'click',
    'menuitemcheckbox', 'menuitemradio', 'a-button-text', 'button-text', 'button-icon', 'button-icon-only', 'button-text-icon-only', 'dropdown', 'combobox'
]

SAFE_ATTRIBUTES = [
	# Standard HTML attributes
	'name',
	'type',
	'value',
	'placeholder',
    'label'
	# Accessibility attributes
	'aria-label',
	'aria-labelledby',
	'aria-describedby',
	'role',
	# Common form attributes
	'for',
	'autocomplete',
	'required',
	'readonly',
	# Media attributes
	'alt',
	'title',
	'src',
	# Data attributes (if they're stable in your application)
	'data-testid',
	'data-id',
	'data-qa',
	'data-cy',
	# Custom stable attributes (add any application-specific ones)
	'href',
	'target',
    # Common Style attributes
    'id',
    'class'
]