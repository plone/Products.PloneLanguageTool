from setuptools import setup, find_packages

version = '3.2.4'

setup(name='Products.PloneLanguageTool',
      version=version,
      description="PloneLanguageTool allows you to set the available "
                  "languages in your Plone site, select various fallback "
                  "mechanisms, and control the use of flags for language "
                  "selection and translations.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone i18n l10n flags',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/Products.PloneLanguageTool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
