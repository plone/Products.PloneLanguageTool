from setuptools import setup, find_packages
import sys, os

version = '2.0.3'

setup(name='Products.PloneLanguageTool',
      version=version,
      description="PloneLanguageTool allows you to set the available "
                  "languages in your Plone site, select various fallback "
                  "mechanisms, and control the use of flags for language "
                  "selection and translations.",
      long_description="""\
      """,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone i18n l10n flags',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/PloneLanguageTool/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://plone.org/products/plonelanguagetool/releases',
      install_requires=[
        'setuptools',
      ],
)
