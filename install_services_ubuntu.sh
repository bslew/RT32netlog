#!/bin/bash
cp RT32logging/save-electric-cabin-data.service /lib/systemd/system/
chown root:root /lib/systemd/system/save-electric-cabin-data.service

systemctl enable save-electric-cabin-data
