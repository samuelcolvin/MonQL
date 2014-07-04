'use strict';

var DbViewer = angular.module('DbViewer', ['ngRoute', 'ngResource', 'DbViewerServices']);

DbViewer.config(['$routeProvider', '$locationProvider', 
  function($routeProvider, $locationProvider) {
    $routeProvider
      .when('/', {
        templateUrl: '/static/partials/index.html?',
        controller: IndexCtrl
      })
      .when('/about', {
        templateUrl: '/static/partials/about.html?',
        controller: AboutCtrl
      })
      .when('/db/:dbid', {
        templateUrl: '/static/partials/details.html?',
        controller: 'DbDetailsCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
      $locationProvider.html5Mode(true);
}]);

// DbViewer.run(function($rootScope) {
//    $rootScope.$on('$routeChangeSuccess', function(ev,data) {   
//      // if (data.$route && data.$route.controller)
//      //   $rootScope.controller = data.$route.controller;
//      console.log("url changed", document.location.pathname);
//    })
// });

angular.module('DbViewerServices', ['ngResource'])
.factory('Database', function($resource){
	return $resource('/api/db/:dbid', {})
});


// DbViewer.controller('DbListCtrl', function ($scope, $http) {
//   $http.get('/api/dbs').success(function(data) {
//     $scope.dbs = data.dblist;
//   });
// });

function DbListCtrl($scope, $http) {
  $http.get('/api/dbs').success(function(data) {
    $scope.dbs = data.dblist;
  });
}

DbViewer.controller('DbDetailsCtrl', ['$scope', '$routeParams', 'Database', 
										function ($scope, $routeParam, Database) {
	var postQuery = Database.get({dbid: $routeParam.dbid}, function(data) {
		$scope.db = data.db;
		console.log(data.db);
	});
}]);

function IndexCtrl($scope) {
}

function AboutCtrl($scope) {}