from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="ptsched",
    version="1.0",
    description="Classwork scheduling tool",
    license="MIT",
    long_description=long_description,
    author="Austin Long",
    author_email="austin@austinlong.dev",
    url="https://austinlong.dev/projects/ptsched",
    packages=["ptsched"],  # same as name
    entry_points={
        "console_scripts": ["ptsched=ptsched.main:main"],
    },
    package_data={"ptsched": ["bin/event-helper"]},
)
