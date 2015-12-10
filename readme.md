# Item Catalog
## Description
This project is submission for Udacity FSND P3. It uses following technologies:
* Python (Flask, sqlalchemy)
* Sqlite database
* AngularJS
* Bootstrap

Flask enables the availability of REST endpoints for communicating with data and rendering of templates and other application's static resource.

## Whats Included?
* catalog
  * db_setup.py
    * Sets up the sqlite database
  * populate_items_categories.py
    * Populates the database to start with some existing items
  * client_secrets.json
    * Contains values needed for Google+ Sign in
  * fb_client_secrets.json
    * Contains values needed for Google+ Sign in
  * app.py
    * Main app which provides the REST Endpoints for client server communication. `python app.py` starts the server and application can be accessed at `http://localhost:5000`
  * itemcatalogwithusers.db (generated automatically once the db_setup.py is run)
  * static
    * angular
      * ... AngularJS files ...
    * bootstrap
      * ... bootstrap files ...
    * css
      * style.css
        * Contains custom styling for application
      * login.css
        * Contains custom styling for login page
    * fonts
      * ... font files ...
    * images
      * noimage.png
        * This image is rendered if there is no image associated with an item
    * js
      * app.js
        * Handles all the client-side functionality using AngularJS. Controllers, Services and custom Directives are defined in this along with URL routing
    * partials
      * items.html
        * This view displays items retreived from server
      * delete-item.html
        * This view confirms whether user wants to delete selected item or not.
      * edit-item.html
        * This view renders a form just like new item page with values for selected item already loaded. user is able to edit the item details or change the image.
      * home.html
        * Contains welcome message with username and profile photo
      * new-item.html
        * Form for adding new item with ability to upload an image
    * uploads
      * uploaded image files are stored here...
  * templates
    * index.html
      * main angularjs based html5 application with navbar, custom alerts and views placeholder
    * login.html
      * Lets the user log in using Google+ or Facebook

## How to setup environment?
Follow the guidelines provided in the [project description][1] to set up the vagrant vm and clone the [fullstack-nanodegree-vm][2] repository. Clone this item catalog project repository to `<path to your local fullstack-nanodegree-vm folder>/vagrant/catalog` folder.

## How to access application?
1. Go to following folder inside the folder where you cloned this repository.
    `cd <path to your local fullstack-nanodegree-vm folder>/vagrant/catalog`
2. Run `python db_setup.py`
3. Run `python populate_items_categories.py`
4. Run `python app.py`
5. Open your web browser and go to `http://localhost:5000`
6. Application's login page will be loaded. Use either of the Google or Facebook to sign in.

## REST Service Response Data Types
Currently, by default REST services return result as JSON objects. But if the request contains `f=xml` parameter, then the result will be in xml format.
example url:
    `http://localhost:5000/categories/all?state=<state token>` returns JSON objects
    `http://localhost:5000/categories/all?state=<state token>&f=xml` returns XML formatted data

## Item Catalog Application Details
* It has 3 major sections i.e. Navbar, Left menu, content area. Navbar and left menu remain unchanged during the runtime but content area has views which keep on changing based on different tasks being performed by user.
* When User logs in successfully, they are greeted with displaying their profile pic.
* If User clicks on any category in left item, content area displays those items with their title, description and price details along with the photo.
* If user has already added any item, they can see the Edit and Delete button below each item. This indicates that user is authorized to change this item. Items added by other users can be viewed but cannot be changed. Thats why Edit and Delete buttons are not displayed.

* When editing, photo will not be updated if the user does not want to upload a new photo.

* Only photo can be changed without changing other details.

* Delete item deletes the photo from filesystem as well

[1]: https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true
[2]: https://github.com/udacity/fullstack-nanodegree-vm
