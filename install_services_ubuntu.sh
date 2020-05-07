#!/bin/bash
cp python/save-electric-cabin-data/save-electric-cabin-data.service /lib/systemd/system/
chown root:root /lib/systemd/system/save-electric-cabin-data.service

systemctl enable save-electric-cabin-data

cp python/save-focus-box-meteo/save-focus-box-meteo.service /lib/systemd/system/
chown root:root /lib/systemd/system/save-focus-box-meteo.service

systemctl enable save-focus-box-meteo


