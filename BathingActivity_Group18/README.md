# SEP769_Group18_BathingAcitivty

This project builds an IoT device using a Raspberry Pi 4 B+ with an LED on pin 17 and an RCWL-0516 microwave sensor on pin 22. 

A quick video overview of the software:

https://www.youtube.com/watch?v=UCYoCJ_yyv4&embeds_referring_euri=https%3A%2F%2Fhubblecontent.osi.office.net%2F&source_ve_path=MjM4NTE

This project contains 3 files:

# 1. BathingActivity_ServerCode_Group18.py
This code will run on your laptop (aka the 'server' or 'client'). This code sets a connection to the database and with the MQTT broker. This code receives published messages from the Raspberry Pi device as JSON data and parses it into discrete data and inserts it into the database.

# 2. SEP769-Prod.db
This would also be placed on your laptop, server or client location. This is an SQLite database containing 1 table. The table contains data for 
- deviceID (unique identifier for the device);
- sentDate (Unix timestamp when the message was sent from the Raspberry Pi);
- startDate (Unix timestamp of when the bath started);
- endDate (Unix timestamp of when the bath ended);
- duration (the difference between endDate and startDate)
- status (the status code of the event the Raspberry Pi recorded)

# 3. BathingActivity_DeviceCode_Group18.py
This code runs on the Raspberry Pi. This code sets up the pins, establishes a connection with the MQTT broker, and has an algorythm for choosing which status to be in - either low power mode (going to 'sleep' for short periods of time and 'waking up' to see if there is activty in the bathroom) or bathing mode (timing how long a bath is happening and checking when it will be over). If there is activity in the bathroom, the algorythm will start timing how long the bath activty is happening for. Once the device stops seeing consistent sensor ativty, the bath is considered over and the summarized data will be published using MQTT.
