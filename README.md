# NOCD
[![Django CI](https://github.com/IPv18/NOCD/actions/workflows/django.yml/badge.svg)](https://github.com/IPv18/NOCD/actions/workflows/django.yml)
## Setup

### Virtual Environment

To start, we need to create a python virtual environment for our project.

- We will be using pip so we need to make sure it is up to date. You can use this command to do that:

    #### Windows
    ```
    py -m pip install --upgrade pip
    ```

    #### Linux
    ```
    python3 -m pip install --user --upgrade pip
    ```

- Then we will need to install virtualenv, the package we will be using to create our virtual environment, run those commands:

    #### Windows
    ```
    py -m pip install --user virtualenv
    ```

    #### Linux
    ```
    python3 -m pip install --user virtualenv
    ```
- Now that we have the virtualenv package we can create our virtual environment like this:

    #### Windows
    ```
    py -m venv .venv
    ```

    #### Linux
    ```
    python3 -m venv .venv
    ```
- Finally, we will activate it like so:

    #### Windows
    ```
    .\.venv\Scripts\activate
    ```

    #### Linux
    ```
    source .venv/bin/activate
    ```

    If you are facing problems activating it on windows it might have to do with the terminal you are using, try doing this instead:
    ```
    source .venv/Scripts/activate
    ```

On your terminal it should now show something like this:
```
(.venv) <--
User@Machine MINGW64 ~/Documents/Homework
```
If it doesn't, try repeating the steps above.

### Insalling requirements.txt

 Now that our virtual environment is working we will need to install some packages on it, there will be a file called ```requirements.txt``` included in the project, if you cannot find it try pulling from the remote repository, or alternitavely try cloning the repository again.

 To install the packages is quite simple, just run this command:

 ```
 pip install -r requirements.txt
 ```

 After that is done you should be ready to run the project.
