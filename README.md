# Mathnasium QR Code Sign-in System
### Author: Shreyas Prasad <contact@shreyasprasad.dev>

## Primary Usage
Modify `.env` file to contain your login information for Radius.

Ex: If your username is `John.Smith` and your password is `MyPassword`, your .env file should look like the following

```
MathnasiumUsername=John.Smith
MathnasiumPassword=MyPassword
```

Run the `main.py` python script by running the `run.bat` batch file.


## QR Code Generation
If you would like to use the provided script to generate QR codes, as opposed to an external service, run `python qrcode_gen.py -h` in the terminal to view the usage.

There are 2 primary use cases for the script:
- Single Student QR Code Generation
- Mass QR Code Generation

### Single Student
For a single student, run: 

`python qrcode_gen.py <Student Name>`

Type the student's name exactly as it would appear on Radius. This will generate a QR Code within the `./img` directory, with the name `<Student Name>.png`.


### Multiple Students
For multiple students, run:

`python qrcode_gen.py -l <file>`

Where file is the directory to a standard text file with student names on each line. Each line must contain ONLY the name of the student, no extra whitespace or text, exactly as it appears on Radius. This will generate a corresponding QR Code for each student within the `./img` directory.