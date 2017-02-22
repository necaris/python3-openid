.PHONY: clean

# Helper function to complete multiple steps in a release -- compute the next
# version, patch the code to embed it, and tag it in Git
define release
	$(eval NEXTVER := $(shell python admin/next_version.py --$(1)))
	python admin/patch_version.py ${NEXTVER}
	git commit -m \"Version $(NEXTVER)\" -- openid/__init__.py # &&
	git tag "v$(NEXTVER)" -m \"Version $(NEXTVER)\"
endef

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +

upload:
	rm -rf dist/*
	python setup.py clean sdist bdist_wheel
	twine upload dist/*

test:
	coverage run -m unittest openid.test.test_suite

release-patch: clean test
	@$(call release,patch)

release-minor: clean test
	@$(call release,minor)

release-major: clean test
	@$(call release,major)

push-tags:
	git push --tags origin HEAD:master

publish: push-tags upload
