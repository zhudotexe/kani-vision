# kani Extension Template

This repository contains a template for building kani extensions that use the `kani.ext.*` namespace.

See https://packaging.python.org/en/latest/tutorials/packaging-projects/ for more information.

## Getting Started

### Create Repo From Template

The first step is to create your own repo using this repo as a template!

Follow the instructions
at https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template
in order to create your repo. We recommend naming your extension repo like `kani-ext-myextension`, but you are free to
choose whatever name you like.

### Choose License

An important next step is to choose your code's license. kani is licensed under the MIT license, which allows extension
developers to license their own code with a license of their own choice.

We (the kani developers) recommend making your extension available under the MIT license as well. You are, however, free
to choose your own license: https://choosealicense.com/

Once you've chosen a license, add it to your repository in a file named `LICENSE`.

### Update Names

Now that you've created your repo, the next step is to change the template names to your own package's names. The files
you'll need to change are:

- `pyproject.toml`: Set your package name and metadata
- `kani/ext/my_extension`: Rename the `my_extension` directory to your own name
- `.github/workflows/pythonpublish.yml` (optional): Set the environment variable to the right PyPI URL

Finally, you can delete the contents of this README and replace them with your own! Write your code in the `kani/ext/*`
package you renamed.

## Publishing to PyPI

To publish your package to PyPI, this repo comes with a GitHub Action that will automatically build and upload new
releases. Alternatively, you can build and publish the package manually.

### GitHub Action

To use the GitHub Action, you must configure it as a publisher for your project on
PyPI: https://pypi.org/manage/account/publishing/

The workflow is configured with the following settings:

- workflow name: `pythonpublish.yml`
- environment name: `pypi`

Once you've configured this, each release you publish on GitHub will automatically be built and uploaded to PyPI.
You can also manually trigger the workflow.

Make sure to update the version number in `pyproject.toml` before releasing a new version!
