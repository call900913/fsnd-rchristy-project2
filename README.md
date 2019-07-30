# Item Catalog Web App

This project is a web app which essentially is a list of items, or an Item Catalog.

To use the app, the User needs to have an account. You can sign up on the site,
or alternatively, you can sign up or login using your Google or Facebook account.

Registered users will have the ability to view, create, edit, or delete items in their list.


## Vagrant

At this phase of the iteration, the app in this directory is to be run in a local environment.

This local environment requires the use of Vagrant.

So before continuing, please download and install [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_2) (pick version 5.2) and [Vagrant](https://www.vagrantup.com).
If you have already downloaded and installed these items, you do not need to download and install them again.

To check whether you have them installed, you can open your Command Line application and enter the command `vagrant --version`.

Following installation, create a directory to house this project.

On your Command Line, navigate to that directory, and run `vagrant init`.


## Next Steps (after Vagrant installation)

Please go over these steps to load the web app on your local machine
(lest the web app may not function properly):


1. Clone the project into the folder discussed in the previous section.
One way of doing this is by visiting this url: [https://github.com/call900913/fsnd-rchristy-project2](https://github.com/call900913/fsnd-rchristy-project2) and clicking on the green `clone or download` button.
Download the project into the aforementioned folder.

2. Navigate to that folder, and type `python database_setup.py` and hit enter.

3. After running `python database_setup.py`, run `python addfirstuser.py`.

4. Still in the same folder and run `vagrant up`.

5. After the completion of the previous step, run `vagrant ssh`.

6. When the Linux terminal has loaded, type `cd /vagrant`.

7. Then, type `ls` and find the project directory -- `cd` into that directory.

8. In the project root directory, on your Command Line type `python app.py` and hit enter.

9. Open a web browser and type in `http://localhost:5000` in the browser's address bar.


## JSON endpoint

The web app features a `JSON endpoint` which can be found here: `http://localhost:5000/categories/JSON`.

Cheers!
