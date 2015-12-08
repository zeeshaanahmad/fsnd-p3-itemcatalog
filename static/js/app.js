var module = angular.module('myapp', ['ngRoute']);

// By default in angularjs, the values in controller scope can be placed anywhere 
// in HTML Pages using double curly brackets like this {{something}} but rendering
// pages from flask conflicts with flask way of parsing such placeholders for context
// variables. In order to make both work, the angularjs module configuration can be
// changed to recognize anyother symbol. So, {{something}} has been replaced with
// {[{something}]}.
module.config(function($interpolateProvider){
  $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
});

// Angular URL Routing configuration, it handles different url patterns and decides
// what to do. It loads required html partial file based on the pattern
module.config(['$routeProvider', function($routeProvider){
  $routeProvider.
  when('/', {
    templateUrl: 'static/partials/home.html',
    controller: 'HomeController'
  }).when('/index', {
    templateUrl: 'static/partials/home.html',
    controller: 'HomeController'
  }).when('/categories/:categoryId/items/all',{
    templateUrl: 'static/partials/items.html',
    controller: 'ItemsController'
  }).when('/categories/:categoryId/items/:itemId',{
    templateUrl: 'static/partials/items.html',
    controller: 'ItemsController'
  }).when('/newitem/category/:categoryId',{
    templateUrl: 'static/partials/new-item.html',
    controller: 'NewItemController'
  }).when('/edit/category/:categoryId/item/:itemId',{
    templateUrl: 'static/partials/edit-item.html',
    controller: 'EditItemController'
  }).when('/delete/category/:categoryId/item/:itemId',{
    templateUrl: 'static/partials/delete-item.html',
    controller: 'DeleteItemController'
  }).otherwise({
    redirectTo: '/index'
  })
}]);

// LoginService is available throughout the application and contains information
// about the login and user. It can check with server if the the login session is
// valid
module.factory('LoginService', function($http) {
  var alerts=[];
  var loggedIn=false;
  var state;
  var username;
  var profile_picture;

  return {
    getState: function(){
      return state;
    },
    setState: function(appState){
      state = appState;
    },
    getUsername: function(){
      return username;
    },
    setUsername: function(name){
      username = name;
    },
    getProfilePicture: function(){
      return profile_picture;
    },
    setProfilePicture: function(pic){
      profile_picture = pic;
    },
    // connects to checkLoggedIn rest endpoint to check if the login session is
    // present
    checkLoggedIn: function(){
      return $http.get('http://localhost:5000/checkLoggedIn?state=' + state);
    },
    setLoggedIn: function() {
      loggedIn = true;
    },
    setLoggedOut: function(){
      loggedIn = false;
    }
  };
});

// HomeController is associated with static/partials/home.html partial and gets
// called when this partial is loaded. It handles the displaying of welcome message
// to user along with their profile picture.
module.controller('HomeController',['$scope', '$http', 'LoginService', function($scope, $http, LoginService) {
  $scope.username = LoginService.getUsername();
  $scope.profile_picture = LoginService.getProfilePicture();
}]);

// It handles the retreival of values from hidden controls and assigns them to
// LoginService properties for later use in the application
module.controller('StateController',['$scope', 'LoginService', function($scope, LoginService) {
  LoginService.setState(document.getElementsByName('state')[0].value);
  LoginService.setUsername(document.getElementsByName('username')[0].value);
  LoginService.setProfilePicture(document.getElementsByName('profile_picture')[0].value);
}]);

// Connects to REST endpoint to retreive all the categories and assigns to $scope
// for building left menu
module.controller('CategoriesController',['$scope', '$http', '$window', 'LoginService',function($scope, $http, $window, LoginService) {
  $http.get('http://localhost:5000/categories/all?state=' + LoginService.getState())
  .success(function (data){
    $scope.data = data;
  })
  .catch(function(err){
    console.error(err);
  })
  .finally(function(){

  });
}]);

// Retreives items from REST endpoint for selected category and loads the
// static/partials/items.html partial
module.controller('ItemsController',['$scope', '$http', '$routeParams', '$window', 'LoginService', 'Alert', '$timeout', function($scope, $http, $routeParams, $window, LoginService, Alert, $timeout){
  $scope.categoryId = $routeParams.categoryId;
  $http.get('http://localhost:5000/categories/' + $routeParams.categoryId + '/items/all?state=' + LoginService.getState())
  .success(function (data){
    // Checks if the items added by current user are present, then builds that
    // user items section, otherwise displays an alert
    if (typeof data.userItems !== 'undefined' && data.userItems.length > 0) {
      $scope.data = data;
    }
    else {
      // Adding an alert
      Alert.addAlert({
        title: 'No items available for current user',
        message: '',
        type: 'errorAlert', // this has to match the alert-type attribute
        alertClass: 'alert-info', //the alert element will have this class, good for css styling
      });

      // It calls the clearAllAlerts method after 3 secs to remove the alert
      // from interface
      $timeout(Alert.clearAllAlerts, 3000);
    }
    // Checks if the items added by other users are present, then builds that
    // user items section, otherwise displays an alert
    if (typeof data.itemsByOtherUsers !== 'undefined' && data.itemsByOtherUsers.length > 0) {
      $scope.data = data;
    }
    else {
      Alert.addAlert({
        title: 'No items added by other users',
        message: '',
        type: 'errorAlert', // this has to match the alert-type attribute
        alertClass: 'alert-info', //the alert element will have this class, good for css styling
      });
      $timeout(Alert.clearAllAlerts, 3000);
    }
  })
  .catch(function(err){
    console.error(err);
  })
  .finally(function(){

  });
}]);


module.controller('NewItemController',['$scope', '$http', '$routeParams',
'$location', 'Alert', '$timeout', 'LoginService', '$window',
function($scope, $http, $routeParams, $location, Alert,
  $timeout, LoginService, $window){
  $scope.categoryId = $routeParams.categoryId;
  // First check if the user is still logged in. If not, redirect to login page
  LoginService.checkLoggedIn().success(function(data) {
  if (data.loggedIn) {

  }
  else{
    $window.location.href = 'http://localhost:5000/login'  // redirect to login
  }
  })
  .error(function (){
    $window.location.href = 'http://localhost:5000/login'
  });

  // When user clicks on the submit button to add new item, this method is called.
  // It posts the data for newly added item to server REST end point along with
  // the photo. Displays an alert on the response and notifies user whether the
  // item was successfully added or not.
  $scope.addItem = function () {
    // Checks if the login session is present, otherwise redirects to login page
    LoginService.checkLoggedIn().success(function(data){
      if (data.loggedIn) {
      $http({
        method: 'POST',
        url: '/newitem/category/' + $routeParams.categoryId + '?state=' + LoginService.getState(),
        headers: {
          'Content-Type': undefined
        },
        data: {
          // Adding user input data to post request
          name: $scope.itemName,
          description: $scope.itemDescription,
          price: $scope.itemPrice,
          file: $scope.file  // file directive's file attribute has the information
          // of the file being uploaded
        },
        // Tranforms the request by converting the data into FormData object so
        // that server can handle file upload along with additional information
        transformRequest: function (data, headersGetter) {
          var formData = new FormData();
          angular.forEach(data, function (value, key) {
            formData.append(key, value);
          });

          // Removes the content type from header, which is taken care of itself
          var headers = headersGetter();
          delete headers['Content-Type'];

          return formData;
        }
      })
      .success(function (data) {
        if (data.added) {
          // if the item is added successfully, server returns added=true, after
          // which the user is redirected to items page by changing the route url and
          // an alert is shown to inform the user.
          $location.path('/categories/' + $routeParams.categoryId + '/items/all')
          Alert.addAlert({
            title: 'Added!',
            message: 'Item has been added successfully.',
            type: 'successAlert', // this has to match the alert-type attribute
            alertClass: 'alert-success', //the alert element will have this class, good for css styling
          });
          $timeout(Alert.clearAllAlerts, 3000); // to remove alert after 3 secs
        }
        else {
          // In case the addition of new item is failed, server returns added=false.
          // Pages redirects to items and dislays an alert to notify the user that
          // item addition failed.
          $location.path('/categories/' + $routeParams.categoryId + '/items/all')
          Alert.addAlert({
            title: 'Adding Failed!',
            message: 'Item could not be added.',
            type: 'errorAlert', // this has to match the alert-type attribute
            alertClass: 'alert-danger', //the alert element will have this class, good for css styling
          });
          $timeout(Alert.clearAllAlerts, 3000);
        }

      })
      .error(function (data, status) {
        $location.path('/categories/' + $routeParams.categoryId + '/items/all')
        Alert.addAlert({
          title: 'Adding Failed!',
          message: 'Item could not be added.',
          type: 'errorAlert', // this has to match the alert-type attribute
          alertClass: 'alert-danger', //the alert element will have this class, good for css styling
        });
        $timeout(Alert.clearAllAlerts, 3000);
      });
    }
    else {
      $window.location.href = 'http://localhost:5000/login'
    }
    })
    .error(function (data, status) {
      $window.location.href = 'http://localhost:5000/login'
    });
  };
}]);

// Handles the editing of an existing item
module.controller('EditItemController',['$scope', '$http', '$routeParams',
'$location', 'Alert', '$timeout', 'LoginService', '$window', '$timeout',
function($scope, $http, $routeParams, $location, Alert, $timeout,
LoginService, $window, $timeout){
  LoginService.checkLoggedIn().success(function(data) { // Check for login session
  if (data.loggedIn) {
  $scope.categoryId = $routeParams.categoryId;
  $scope.itemId = $routeParams.itemId;
  // Load the selected from database on the editing form
  $http.get('http://localhost:5000/categories/' + $routeParams.categoryId +
  '/items/' + $routeParams.itemId + '?state=' + LoginService.getState())
  .success(function (data){
    if (typeof data.items !== 'undefined' && data.items.length > 0) {
      $scope.itemName = data.items[0].name;
      $scope.itemDescription = data.items[0].description;
      $scope.itemPrice = data.items[0].price;
      $scope.image_src = data.items[0].image_src;
    }
  else {
    // If no item found, show alert
    $location.path('/categories/' + $routeParams.categoryId + '/items/all')
    Alert.addAlert({
      title: 'Error',
      message: 'No items to update',
      type: 'errorAlert', // this has to match the alert-type attribute
      alertClass: 'alert-danger', //the alert element will have this class, good for css styling
    });
    $timeout(Alert.clearAllAlerts, 3000);
  }
  })
  .catch(function(err){
    console.error(err);
  })
  .finally(function(){

  });
}
else {
  $window.location.href = 'http://localhost:5000/login'
}
}).error(function (){
  $window.location.href = 'http://localhost:5000/login'
});

  // Calls when the user submits the form after editing the item
  $scope.editItem = function () {
    // First checks if the login session is present
    LoginService.checkLoggedIn().success(function(data) {
    if (data.loggedIn) {
    var data = {};
    // if current edits contain a change to file, only then upload the file,
    // otherwise keep it as is
    if ($scope.file) {
      data = {
        name: $scope.itemName,
        description: $scope.itemDescription,
        price: $scope.itemPrice,
        file: $scope.file
      };
    }
    else {
      data = {
        name: $scope.itemName,
        description: $scope.itemDescription,
        price: $scope.itemPrice,
        file: null
      };
    }
    $http({
      method: 'POST',
      url: '/edititem/category/' + $routeParams.categoryId + '/item/' + $routeParams.itemId + '?state=' + LoginService.getState(),
      headers: {
        'Content-Type': undefined
      },
      data: data,
      transformRequest: function (data, headersGetter) {
        var formData = new FormData();
        angular.forEach(data, function (value, key) {
          formData.append(key, value);
        });

        var headers = headersGetter();
        delete headers['Content-Type'];

        return formData;
      }
    })
    .success(function (data) {
      if (data.updated) {
        // redirects to all items page and shows success alert
        $location.path('/categories/' + $routeParams.categoryId + '/items/all')
        Alert.addAlert({
          title: 'Updated!!',
          message: 'Item has been updated successfully.',
          type: 'successAlert', // this has to match the alert-type attribute
          alertClass: 'alert-success', //the alert element will have this class, good for css styling
        });
        $timeout(Alert.clearAllAlerts, 3000);
      }
      else {
        //$location.path('/categories/' + $routeParams.categoryId + '/items/all')
        // remains on the same edit page and shows alerts that editing failed
        Alert.addAlert({
          title: 'Update Failed!',
          message: data.msg,
          type: 'errorAlert', // this has to match the alert-type attribute
          alertClass: 'alert-danger', //the alert element will have this class, good for css styling
        });
        $timeout(Alert.clearAllAlerts, 3000);
      }
    })
    .error(function (data, status) {
      Alert.addAlert({
        title: 'Update Failed!',
        message: data.msg,
        type: 'errorAlert', // this has to match the alert-type attribute
        alertClass: 'alert-danger', //the alert element will have this class, good for css styling
      });
      $timeout(Alert.clearAllAlerts, 3000);
    });
  }
  else {
    $window.location.href = 'http://localhost:5000/login'
  }
  }).error(function (data, status) {
    $window.location.href = 'http://localhost:5000/login'
  });
  };
}]);

module.controller('DeleteItemController',['$scope', '$http', '$routeParams',
'$location', 'Alert', '$timeout', 'LoginService', '$window', '$timeout',
function($scope, $http, $routeParams, $location, Alert, $timeout,
  LoginService, $window, $timeout){
  $scope.categoryId = $routeParams.categoryId;
  $scope.itemId = $routeParams.itemId;

  LoginService.checkLoggedIn().success(function(data) { // Check login
  if (data.loggedIn) {
    $http.get('http://localhost:5000/categories/' + $routeParams.categoryId +
    '/items/' + $routeParams.itemId + '?state=' + LoginService.getState())
    .success(function (data){ // check if item is present
      if (typeof data.items !== 'undefined' && data.items.length > 0) {
        $scope.itemName = data.items[0].name;
        $scope.itemDescription = data.items[0].description;
        $scope.itemPrice = data.items[0].price;
        $scope.image_src = data.items[0].image_src;
      }
      else {
        // Show an alert if item to be deleted is not available
        $location.path('/categories/' + $routeParams.categoryId + '/items/all')
        Alert.addAlert({
          title: 'Error',
          message: 'No items to delete',
          type: 'errorAlert', // this has to match the alert-type attribute
          alertClass: 'alert-danger', //the alert element will have this class, good for css styling
        });
        $timeout(Alert.clearAllAlerts, 3000);
      }
    })
    .catch(function(err){
      console.error(err);
      Alert.addAlert({
        title: 'Error',
        message: 'There has been an error while retreiving information.',
        type: 'errorAlert', // this has to match the alert-type attribute
        alertClass: 'alert-danger', //the alert element will have this class, good for css styling
      });
    })
    .finally(function(){

    });
  }
  else{
    $window.location.href = 'http://localhost:5000/login'
  }
  })
  .error(function (){
    $window.location.href = 'http://localhost:5000/login'
  });


// If user cancels the delete, redirects to all items
  $scope.cancel = function () {
    $location.path('/categories/' + $routeParams.categoryId + '/items/all')
  };
// Handles deleting of an item
  $scope.deleteItem = function () {
    LoginService.checkLoggedIn().success(function(data) { // Checks login
    if (data.loggedIn) {
      $http.get('http://localhost:5000/deleteitem/category/' + $routeParams.categoryId + '/item/' + $routeParams.itemId + '?state=' + LoginService.getState())
      .success(function (data){ // If deleted, Show success alert and redirect
        if (data.deleted){
          $location.path('/categories/' + $routeParams.categoryId + '/items/all')
          Alert.addAlert({
            title: 'Deleted!',
            message: 'Item has been deleted successfully.',
            type: 'successAlert', // this has to match the alert-type attribute
            alertClass: 'alert-success', //the alert element will have this class, good for css styling
          });
          $timeout(Alert.clearAllAlerts, 3000);
        }
        else {
          // Notify user that item deletion failed
          $location.path('/categories/' + $routeParams.categoryId + '/items/all')
          Alert.addAlert({
            title: 'Delete Failed!',
            message: 'Item could not be deleted.',
            type: 'errorAlert', // this has to match the alert-type attribute
            alertClass: 'alert-danger', //the alert element will have this class, good for css styling
          });
          $timeout(Alert.clearAllAlerts, 3000);
        }
      })
      .catch(function(err){
        console.error(err);
        Alert.addAlert({
          title: 'Error',
          message: 'Item could not be deleted.',
          type: 'errorAlert', // this has to match the alert-type attribute
          alertClass: 'alert-danger', //the alert element will have this class, good for css styling
        });
        $timeout(Alert.clearAllAlerts, 3000);
      })
      .finally(function(){
        // $timeout(Alert.clearAllAlerts(), 5000);
      });
    }
    else{
      $window.location.href = 'http://localhost:5000/login'
    }
    })
    .error(function (){
      $window.location.href = 'http://localhost:5000/login'
    });


  };
}]);

// Custom angularjs directive to handle file upload
module.directive('file', function () {
  return {
    scope: {
      file: '='
    },
    link: function (scope, el, attrs) {
      el.bind('change', function (event) {
        var file = event.target.files[0];
        scope.file = file ? file : undefined;
        scope.$apply();
      });
    }
  };
});

// Custom angularjs Alert service, which handles adding/clearing alerts
module.factory('Alert', function ($rootScope) {
  var alerts=[];
  return {
    getAlerts: function(){
      return alerts;
    },
    addAlert: function(alertData) {
      alerts.push(alertData);
    },
    removeAlert: function(alert){
      var index = alerts.indexOf(alert);
      alerts.splice(index,1)
    },
    clearAllAlerts: function() {
      alerts=[];
    },
  };
});
// Custom directive to display alerts on the page
module.directive('customAlerts', function (Alert, $timeout) { //injects the Alert serivce
  return {
    scope: {
      alertType: '@?',
    },
    // angularjs renders this template in place of an customAlerts directive and
    // uses Alert service properties to display the message
    template:'<div ng-repeat="alert in alertSrvs.getAlerts()" >\
    <div ng-show="!alertType || alertType===alert.type" class="alert " ng-class="alert.alertClass" role="alert">\
    <strong>{{alert.title}}</strong> {{alert.message}}\
    <button  type="button" class="close"  ng-click="alertSrvs.removeAlert(alert);">\
    <span >&times;</span>\
    </button>\
    </div>\
    </div>',
    restrict: 'EA',
    link: function (scope, element, attrs) {
      scope.alertSrvs=Alert;
    }
  };
});
