# BadgeLink

BadgeLink is a protocol for communicating with Tanmatsu over USB. It allows you to manage apps, settings and files on the device via WebUSB applications in Chromium based browsers or a Python script.

## Downloading the tools

You can find the Python script on the [releases](https://github.com/badgeteam/esp32-component-badgelink/releases) page of the BadgeLink repository. Download the `tools.zip` artifact and unzip it into a folder.

Make sure Python is installed on your computer.

## Installing the tools

A bash shell script has been provided to automatically create a Python virtual environment and install the required libraries into the environment. On Linux and Mac machines you can run this script to automate the process.

On Windows you can manually create the virtual environment by running the following commands in a command window:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Permissions for accessing the USB device on Linux

Copy the `60-badgelink.rules` file to `/etc/udev/rules.d` on your system. Then reload the udev rules and trigger re-detection of hardware.

```
sudo cp 60-badgelink.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Running the BadgeLink tool

On Linux and Mac the `badgelink.sh` script automatically starts the `badgelink.py` script in the virtual environment. On Windows you have to manually enable the virtual environment as follows:

```
source .venv/bin/activate
python badgelink.py
```

## Using the BadgeLink tool

Make sure your Tanmatsu is set to `USB device mode`, by default the USB interface is set to debugging mode and you can change the mode easily by pressing the purple diamond key (second button from the top right of the keyboard). It might take a second before the icon changes but the icon on the top right of the screen will change from the bug to an USB icon to indicate that the USB port mode has been switched.

In the next sections we assume you are using the `badgelink.sh` script. If you are using Windows replace `badgelink.sh` in the commands below with `python badgelink.py` and make sure the virtual envirotnment is active in the command window you are using.

### AppFS

#### Listing installed applications

```
./badgelink.sh appfs list
```

This command will list all the application binaries currently installed into the AppFS partition of the flash chip.

Example output:

```
slug        | title       | version | size 
------------+-------------+---------+------
konsool64   | Konsool 64  | 1       | 833K 
synthwave   | Synthwave   | 1       | 438K 
coprocessor | Coprocessor | 1       | 1063K
```

In this context `slug` is a lowercase ascii string without spaces, formatted in such a way to ensure the name can be used as filename. The `slug` is used for coupling the binary in AppFS with its related files on the FAT partition of flash or the SD card in the `/apps/<slug>/` folder. The `slug` filename needs to be unique for every file in the AppFS.

The `title` field is a human readable name for the application, this string is visible in the menu and you can safely use uppercase letters and spaces in this string.

The `version` field contains an integer number used to couple the version of the installed binary in AppFS to the version of its related files on the FAT partition.

The `size` field contains the size of the application binary in kilobyte.

#### View partition size and usage

```
./badgelink.sh appfs usage
```

This command gives you information on the size of the AppFS partition and the amount of space in use by the installed applications.

Example output:

```
Usage: 2432K / 8128K (29.9%)
```

#### Deleting an application

```
./badgelink.sh appfs delete synthwave
```

The last argument in this command is the `slug` filename of the app you want to remove from AppFS, you can find the `slug` filename using the list command.

#### Copying an app from the device to your computer

```
./badgelink.sh appfs download konsool64 konsool64.bin
```

This command transfers a file on the AppFS partition to your computer. The last two arguments are the `slug` filename of the app and the filename of the output file on your computer.

#### Copying an app from your computer to the device

```
./badgelink.sh appfs upload test "An example app" 123 firmware.bin
```

This command transfers a file on your computer to the AppFS partition. The argumens are the `slug` filename you want the application to have, this name has to be unique, followed by the `title` of the app, in the example above quotes were added around the string to allow the use of spaces. After that comes the `version` argument, an integer number, when testing you can use any number you want, for example `0`. And the last argument is the filename of the firmware binary you want to upload to the device.

If you have just compiled the example app, take a look in the build folder to find the `firmware.bin` file. This file is the only file you need for installing your app.

#### Starting an app

To start an app on the AppFS partition you can use the `start` command:

```
./badgelink.sh start synthwave
```

In which the `synthwave` argument is the slug name of the app to start.

### NVS (Non-volitile storage)

NVS is a partition on the flash which contains a key-value store for settings. Using BadgeLink you can list which keys are in use and read, write and delete the entries.

#### Listing keys in use

```
./badgelink.sh nvs list
```

This command lists all the keys in use. To limit the results to a specific namespace the name of the namespace can be added as an extra argument.

Example output:

```
namespace | key          | type  
----------+--------------+-------
wifi      | s00.ssid     | string
wifi      | s00.password | string
wifi      | s00.identity | string
wifi      | s00.username | string
wifi      | s00.authmode | u32   
wifi      | s00.phase2   | u32   
system    | ntp          | u8    
system    | timezone     | string
system    | tz           | string
wifi      | s01.ssid     | string
wifi      | s01.password | string
wifi      | s01.identity | string
wifi      | s01.username | string
wifi      | s01.authmode | u32   
wifi      | s01.phase2   | u32
```

#### Reading an entry

```
./badgelink.sh nvs read system timezone string
```

To read an entry you specify the namespace, key and type of the entry you want to read. The tool then returns you the value.

```
type: NvsValueString
stringval: "Europe/Amsterdam"

'Europe/Amsterdam'
```

#### Writing an entry

```
./badgelink.sh nvs write test example string "Hello world"
```

The example command above creates or overwrites an entry in the namespace `test`, with key `example` and type `string`. The value `Hello world` gets written into the entry.


#### Deleting an entry

```
./badgelink.sh nvs delete test example
```

The example command above deletes the entry `example` in the namespace `test`.

### FAT filesystem

The internal FAT filesystem partition and the SD card contents can also be manipulated using the BadgeLink tool.

The internal FAT partition on the flash chip is mounted at `/int` and the SD card is mounted at the path `/sd`.

#### Listing the contents of a directory

To list the contents of the root of the internal flash chip filesystem you can run

```
./badgelink.sh fs list /int
```

This results in for example the following output:

```
type | path 
-----+------
dir  | icons
```

Type can be `dir` for a directory and `file` for a file.

#### File statistics

To query statistics for a specific file you can use the `stat` command:

```
./badgelink.sh fs stat /int/icons/menu/wifi_0.png
```

This gives you information about the size of the file and the timestamps for creation, modification and last access. Note that the timestamps have a high chance of not being accurate. If the timestamp is unavailable you will most likely see 1970-01-01 as the date.

```
Type:     file
Size:     539
Created:  1970-01-01 01:00:00
Modified: 1980-01-01 00:00:00
Accessed: 1970-01-01 01:00:00
```

#### Creating a directory

```
./badgelink.sh fs mkdir /int/example
```

Creates a directory called `example` in the root of the internal flash FAT filesystem.

#### Removing a directory

```
./badgelink.sh fs rmdir /int/example
```

Removes a directory called `example` from the root of the internal flash FAT filesystem.

#### Uploading a file from your computer to the device

To send a file to the device you can use the `upload` command.

```
echo "Hello world" > example.txt
./badgelink.sh fs upload /int/example.txt example.txt
```

#### Downloading a file from the device to your computer

To retrieve a file from the device you can use the `download` command.

```
./badgelink.sh fs download /int/example.txt downloaded_file.txt
```

