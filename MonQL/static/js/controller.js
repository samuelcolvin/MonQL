'use strict';

var ConViewer = angular.module('ConViewer', ['ngRoute', 'ngResource']);

ConViewer.config(['$routeProvider', '$locationProvider', 
	function($routeProvider, $locationProvider) {
		$routeProvider
			.when('/', {
				templateUrl: '/static/partials/index.html?',
				controller: IndexCtrl
			})
			.when('/addcon', {
				templateUrl: '/static/partials/edit.html?',
				controller: EditConCtrl
			})
			.when('/editcon/:conid', {
				templateUrl: '/static/partials/edit.html?',
				controller: EditConCtrl
			})
			.when('/about', {
				templateUrl: '/static/partials/about.html?',
				controller: AboutCtrl
			})
			.when('/con/:conid', {
				templateUrl: '/static/partials/details.html?',
				controller: 'ConDetailsCtrl'
			})
			.otherwise({
				redirectTo: '/'
			});
			$locationProvider.html5Mode(true);
}]);

// angular.module('ConViewerServices', ['ngResource'])
// .factory('Database', function($resource){
// 	return $resource('/api/con/:conid', {});
// });

function HeadCtrl($scope, $http) {
	$scope.update = function(){
		$http.get('/api/cons?').success(function(data) {
			$scope.cons = data.cons;
		});
	};
	$scope.update();

	$scope.$on('update-cons', function(event, args) {
		$scope.update();
	});

	$scope.$on('set-conid', function(event, conid) {
		$scope.conid = conid.toString();
	});

	$scope.$on('set-active', function(event, active) {
		$scope.active = active;
	});
}

function MsgCtrl($scope, $http) {
  $scope.success = function(msg){
    $scope.success_msg = msg;
  };
  $scope.success(false);
  var keepmsg = false;

  $scope.$on('success', function(event, msg, persist) {
    console.log('success msg:', msg);
    keepmsg = persist;
    $scope.success(msg);
  });

  $scope.$on('set-active', function(event, active) {
    if (!keepmsg){
      $scope.success(false);
    }
    keepmsg = false;
  });
}

function ConDetailsCtrl($scope, $rootScope, $http, $routeParams) {
	$rootScope.$broadcast('set-active', 'view-con');
	var conid = $routeParams.conid;
	$rootScope.$broadcast('set-conid', conid);
	$scope.conid = conid;
  var gottree = false;
  $scope.show_tree = function(){
    if (!gottree){
      populatetree();
      gottree = true;
    }
    return true;
  };
	$http.get('/api/condef/' + conid).success(function(data) {
		$scope.con = data.con;
	});

	$scope.testconnection = function(con){
    testconnection(con, $http);
	};
	setheight();
}

function IndexCtrl($scope, $rootScope, $http) {
	$rootScope.$broadcast('set-active', '');
	$http.get('/api/cons?').success(function(data) {
		$scope.cons = data.cons;
	});
}

var default_ports = {MongoDB: 27017, MySQL: 3306, PostgreSQL: 5432};

function response_error(prefix, data){
    var msg = prefix;
    if (typeof(data.error) == 'string'){
      msg += data.error;
    }
    bootbox.alert(msg);
}

function EditConCtrl($scope, $rootScope, $http, $routeParams, $location) {
	$scope.master = {host: 'localhost', 'port': '0'};
	var edit = typeof($routeParams.conid) == 'string';
	$scope.saved = edit;

  $scope.reset = function() {
    $scope.con = angular.copy($scope.master);
  };

	if (edit){
		$http.get('/api/condef/' + $routeParams.conid).success(function(data) {
			$scope.master = data.con;
			$scope.reset();
		});
	}
	else {
		$rootScope.$broadcast('set-active', 'add-con');
    $scope.reset();
	}

	$scope.save = function(con) {
		angular.extend($scope.master, con);
		console.log('updated: ', con);
		var response = $http.post("/api/submitcon", $scope.master, {});
		response.success(function(data, status, headers, config) {
			$scope.master = data.data;
      $rootScope.$broadcast('success', $scope.saved ? 'Connection Updated' : 'Connection Saved', false);
			$scope.saved = true;
			$rootScope.$broadcast('update-cons');
		});
		response.error(function(data, status, headers, config) {
      response_error('Error submitting form: ', data);
		});
	};

  $scope.delete = function(con){
    console.log('delete: ', con);
    var response = $http.get("/api/delete/" + $scope.master.id);
    response.success(function(data, status, headers, config) {
      console.log('connection delete');
      $rootScope.$broadcast('update-cons');
      $location.path('/');
      $rootScope.$broadcast('success', 'Deleted Connection ' + $scope.master.id + ' (' + con.ref + ')', true);
    });
    response.error(function(data, status, headers, config) {
      response_error('Error deleting connection: ', data);
    });
  };

	$scope.testconnection = function(con){
    testconnection($scope.master, $http);
	};

	$scope.change_type = function(con){
		con.port = default_ports[con.dbtype];
	};
}

function AboutCtrl($rootScope) {
	$rootScope.$broadcast('set-active', 'about');
}

function testconnection(con, $http){
  var response = $http.get("/api/testcon/" + con.id);
  response.success(function(response) {
    console.log(response);
    var msg = 'Connection Test results: \n<pre>\n' + response + '\n</pre>';
    bootbox.alert(msg);
  });
  response.error(function(data) {
    response_error('Error testing connection: ', data);
  });
}