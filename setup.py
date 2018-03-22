from setuptools import setup, find_packages

<<<<<<< HEAD
=======

>>>>>>> a33f6e815f4183535117df4d83c6b3c187862745
def readme():
    with open('README.md') as f:
        return f.read()

<<<<<<< HEAD
setup(
    name='wishful_final_showcase',
=======

setup(
    name='final_showcase',
>>>>>>> a33f6e815f4183535117df4d83c6b3c187862745
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
<<<<<<< HEAD
    author='Piotr Gawlowicz, Mikolaj Chwalisz,  Anatolij Zubow',
    author_email='{gawlowicz, chwalisz, zubow}@tkn.tu-berlin.de',
    description='WiSHFUL Final Showcase',
    long_description='WiSHFUL Final Showcase',
    keywords='wireless final showcase',
    install_requires=['pyyaml', 'docopt', 'jsocket', 'oml4py']
=======
    author='Peter Ruckebusch',
    author_email='peter.ruckebusch@ugent.be',
    description='WiSHFUL Final Showcase',
    long_description='WiSHFUL Final Showcase',
    keywords='wireless control',
    install_requires=['pyyaml', 'docopt']
>>>>>>> a33f6e815f4183535117df4d83c6b3c187862745
)
