createdb safecity -T template_postgis
./manage syncdb
./manage load_srids
./manage load_centerline -t
./manage load_aliases