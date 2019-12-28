# how to set up
If you don't have virtualenvwrapper

```shell
pip install virtualenvwrapper 
```

Make a virtual environment

```shell
mkvirtualenv -p python3 ENVNAME
```

Change the environment to that virtual environment you just created

```shell
workon ENVNAME
```

Under the virtual environment install requirements

```shell
pip install -r requirements
```



Project using MySQL, Redis and Django