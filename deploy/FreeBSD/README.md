### System V rc script for FreeBSD

Copy the file in `/usr/local/etc/rc.d`

```
# cp /path/to/funkwhale/deploy/FreeBSD/funkwhale_* /usr/local/etc/rc.d
```

If not add executable bit to the files.

```
# chmod +x /usr/local/etc/rc.d/funkwhale_*
```

Enable services in rc.conf

```
# sysrc funkwhale_server=YES
# sysrc funkwhale_worker=YES
# sysrc funkwhale_beat=YES
```
