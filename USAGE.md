# Installation

    virtualenv .
    pip install -r deps.txt
  

# Update

  . bin/activate
  # change your shitz in content/posts
  pelican content -o output -s pelicanconf.py
  ghp-import output
  git push --all
