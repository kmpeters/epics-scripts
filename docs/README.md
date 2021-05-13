# Documentation
The less-fun and more-important part of development.

## makeIOC.sh

A makeIOC.sh-like IOC can be created using [mkioc](https://github.com/BCDA-APS/mkioc) and [configIOC.py](configIOC.md)

```
$ mkioc -f -n -s 6-1 zzz && cd zzz && configIOC.py linux
```

## configIOC.py

[configIOC.py](configIOC.md) is a script that makes it easy to prune unneeded files from an IOC created with [mkioc](https://github.com/BCDA-APS/mkioc)

