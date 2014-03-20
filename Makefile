.PHONY: flake8 example test coverage translatable_strings update_translations

flake8:
	flake8 django_history example tests

example:
	DJANGO_SETTINGS_MODULE=example.settings \
		django-admin.py runserver

test:
	DJANGO_SETTINGS_MODULE=tests.settings \
		django-admin.py test tests

test_selenium:
	DJANGO_SELENIUM_TESTS=true DJANGO_SETTINGS_MODULE=tests.settings \
		django-admin.py test tests

coverage:
	coverage erase
	DJANGO_SETTINGS_MODULE=tests.settings \
		coverage run --branch --source=django_history `which django-admin.py` test tests
	coverage html

translatable_strings:
	cd django_history && django-admin.py makemessages -l en --no-obsolete
	@echo "Please commit changes and run 'tx push -s' (or wait for Transifex to pick them)"

update_translations:
	tx pull -a --minimum-perc=10
	cd django_history && django-admin.py compilemessages
