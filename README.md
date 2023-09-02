# **CPU Badminton Hall automatic reservation**

## Welcome to the Badminton Hall Reservation Program! This app is designed to simplify and manage the badminton hall booking process.

![2023校长杯羽毛球赛](/headmaster.jpg)

## Features
 - User registration and login account 
 - Check availability of badminton courts 
 - Reserve a badminton court for a specific time slot 
 - View your booking history Cancel booked time slots
## Intall and run
 - Clone this repository: 
```
git clone https://github.com/clearbob999/CPU_badminton_reserve.git
```
 - A yaml file containing all requirements is provided. This can be readily setup using conda.
 ```
conda env create -f badminton_reserve.yaml
conda activate gym
```
 - Go to the project directory: 
 ```
cd CPU_badminton_reserve
```
 - Run the command 
```
python badminton.py --start_time 12:00 --end_time 13:00 --ground 5号 --date 周一 --name 胡图图 --telephone 4008823823 --student_ID 3322****** --password ****** --situation True --headless False
```
## Instructions for use
 - Register or log in to your account. 
 - Browse available badminton courts and times. 
 - Select the time slot you would like to book and submit your appointment. 
 - Cancel or modify an appointment (if required) before the scheduled time.

## Copyright and Licensing
**Figure Yile**
