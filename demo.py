from modules import ConnectDB
from flask import Flask, request, render_template, jsonify
import logging
from logger import logging

c= ConnectDB()
c.connect_to_db
l=c.find_available_buses(source='Los Angeles', destination='San Francisco',travel_date='2025-07-16')
print(l[0]['ScheduleID'])