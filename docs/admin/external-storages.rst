Using external storages to store Funkwhale content
==================================================

By default, Funkwhale will store user-uploaded and related media such as audio files,
transcoded files, avatars and album covers on a server directory.

However, for bigger instances or more complex deployment scenarios, you may want
to use distributed or external storages.

S3 and S3-compatible servers
----------------------------

.. note::

    This feature was released in Funkwhale 0.19 and is still considered experimental.
    Please let us know if you see anything unusual while using it.

Funkwhale supports storing media files Amazon S3 and compatible implementations such as Minio or Wasabi.

In this scenario, the content itself is stored in the S3 bucket. Non-sensitive media such as
album covers or user avatars are served directly from the bucket. However, audio files
are still served by the reverse proxy, to enforce proper authentication.

To enable S3 on Funkwhale, add the following environment variables::

    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    AWS_STORAGE_BUCKET_NAME=
    # An optional bucket subdirectory were you want to store the files. This is especially useful
    # if you plan to use share the bucket with other services
    # AWS_LOCATION=

    # If you use a S3-compatible storage such as minio, set the following variable
    # the full URL to the storage server. Example:
    #   AWS_S3_ENDPOINT_URL=https://minio.mydomain.com
    # AWS_S3_ENDPOINT_URL=

Then, edit your nginx configuration. On docker setups, the file is located at ``/srv/funkwhale/nginx/funkwhale.template``,
and at ``/etc/nginx/sites-available/funkwhale.template`` on non-docker setups.

Replace the ``location /_protected/media`` block with the following::

    location ~ /_protected/media/(.+) {
        internal;
        proxy_pass $1;
    }

Then restart Funkwhale and nginx.

From now on, media files will be stored on the S3 bucket you configured. If you already
had media files before configuring the S3 bucket, you also have to move those on the bucket
by hand (which is outside the scope of this guide).

.. note::

    At the moment, we do not support S3 when using Apache as a reverse proxy.

Serving audio files directly from the bucket
********************************************

Depending on your setup, you may want to serve audio fils directly from the S3 bucket
instead of proxying them through Funkwhale, e.g to reduce the bandwidth consumption on your server,
or get better performance.

You can achieve that by adding ``PROXY_MEDIA=false`` to your ``.env`` file.

When receiving a request on the stream endpoint, Funkwhale will check for authentication and permissions,
then issue a 302 redirect to the file URL in the bucket.

This URL is actually be visible by the client, but contains a signature valid only for one hour, to ensure
no one can reuse this URL or share it publicly to distribute unauthorized content.

.. note::
   
   If you are using Amazon S3, you will need to set your ``AWS_S3_REGION_NAME`` in the ``.env`` file to
   use this feature. 

.. note::

    Since some Subsonic clients don't support 302 redirections, Funkwhale will ignore
    the ``PROXY_MEDIA`` setting and always proxy file when accessed through the Subsonic API.


Securing your S3 bucket
***********************

It's important to ensure your the root of your bucket doesn't list its content,
which is the default on many S3 servers. Otherwise, anyone could find out the true
URLs of your audio files and bypass authentication.

To avoid that, you can set the following policy on your bucket::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                "*"
                ]
            },
            "Resource": [
                "arn:aws:s3:::<yourbucketname>/*"
            ],
            "Sid": "Public"
            }
        ]
    }

If you are using ``awscli``, you can store this policy in a ``/tmp/policy`` file, and
apply it using the following command::

    aws s3api put-bucket-policy --bucket <yourbucketname> --policy file:///tmp/policy
