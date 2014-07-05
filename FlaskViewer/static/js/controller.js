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
		$http.get('/api/cons').success(function(data) {
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

function ConDetailsCtrl($scope, $rootScope, $http, $routeParams) {
	$rootScope.$broadcast('set-active', 'view-con');
	var conid = $routeParams.conid;
	$rootScope.$broadcast('set-conid', conid);
	$scope.conid = conid;
	$http.get('/api/condef/' + conid).success(function(data) {
		$scope.con = data.con;
	});
}

function IndexCtrl($rootScope) {
	$rootScope.$broadcast('set-active', '');
}

var default_ports = {MongoDB: 27017, MySQL: 3306};

function EditConCtrl($scope, $rootScope, $http, $routeParams) {
	$scope.master = {host: 'localhost', 'port': '0'};
	var edit = typeof($routeParams.conid) == 'string';
	$scope.saved = edit;

  $scope.reset = function() {
    $scope.con = angular.copy($scope.master);
  };

	if (edit){
		$rootScope.$broadcast('set-active', 'edit-con');
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
			$scope.success = 'Settings saved';
			$scope.saved = true;
			$rootScope.$broadcast('update-cons');
		});
		response.error(function(data, status, headers, config) {
			var msg = 'Error submitting form: ';
			if (typeof(data.error) == 'string'){
				msg += data.error;
			}
			bootbox.alert(msg);
		});
	};

	$scope.testconnection = function(con){
    var response = $http.get("/api/testcon/" + $scope.master.id);
    response.success(function(response, status, headers, config) {
      console.log(response);
      var msg = 'Connection Test results: \n<pre>\n' + response + '\n</pre>';
      bootbox.alert(msg);
    });
    response.error(function(data, status, headers, config) {
      var msg = 'Error testing connection: ';
      if (typeof(data.error) == 'string'){
        msg += data.error;
      }
      bootbox.alert(msg);
    });
	};

	$scope.change_type = function(con){
		con.port = default_ports[con.type];
	};
}

function AboutCtrl($rootScope) {
	$rootScope.$broadcast('set-active', 'about');
}

function page(){
	return 'addcon';
}