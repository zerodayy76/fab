#!/bin/bash

# Restart Gunicorn processes managed by Supervisor
sudo supervisorctl restart guni:*

# Restart Nginx service
sudo service nginx restart
