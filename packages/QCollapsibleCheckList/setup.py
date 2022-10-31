from setuptools import setup

setup(
   name='QCollapsibleCheckList',
   version='0.0.1',
   description='Collapsible checklist implemented in PyQt6',
   author='Li, Mengxun',
   author_email='mengxunli@whu.edu.cn',
   packages=['QCollapsibleCheckList'],  #same as name
   include_package_data=True,
   install_requires=["PyQt6"], #external packages as dependencies
)

