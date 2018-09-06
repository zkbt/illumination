# playground

These are some tools for playing around with early TESS pixels. Documentation can be found at [zkbt.github.io/tv/](https://zkbt.github.io/tv/)

### Installation
You can clone this into your own space and install directly from that editable package. From some base directory where you like to store code, run
```
git clone git@tessgit.mit.edu:zkbt/playground.git
cd playground/
pip install -e .
# or, if you don't have root access ...
pip install -e . --user

```
This will download the current `playground` repository to your current directory, and then link the installed version of the `playground` package to this local repository. Changes you make to the code in the repository should be reflected in the version Python sees when it tries to `import playground` or anything `from` that.
