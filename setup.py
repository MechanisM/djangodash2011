from distutils.core import setup

setup(name='staste',
      version='0.1.1d',
      description="Slightly complicated event tracker for your Django website.",
      author='Valentin Golev',
      author_email='v.golev@gmail.com',
      url='http://staste.unfoldthat.com/',
      packages=['staste', 'staste.charts'],
      package_data={'staste':
                        ['templates/staste/*.html',
                         'templates/staste/*/*.html']
                    },
     )
