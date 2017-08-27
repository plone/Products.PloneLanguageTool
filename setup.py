from setuptools import setup, find_packages

version = '3.2.9'

tests_require = ['Products.CMFTestCase', ]

setup(
    name='Products.PloneLanguageTool',
    version=version,
    description="PloneLanguageTool allows you to set the available "
                "languages in your Plone site, select various fallback "
                "mechanisms, and control the use of flags for language "
                "selection and translations.",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Zope CMF Plone i18n l10n flags',
    author='Hanno Schlichting',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/Products.PloneLanguageTool',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
    ],
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
)
