### Gentoo init scripts 

Copy the files to  `/etc/init.d/`

```
# cp /path/to/scripts/funkwhale_* /etc/init.d/
```

Make the files executable:

```
# chmod +x /etc/init.d/funkwhale_*
```

Starting funkwhale_server will automatically start the other two, as well as nginx and redis.

```
# rc-service funkwhale_server start
```