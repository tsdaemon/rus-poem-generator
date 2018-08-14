'use strict';

angular.module('poetry', [])
.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}])
.controller('poemGeneration', function($scope, $http) {
  $scope.poets = [
    'pushkin',
    'esenin',
    'mayakovskij',
    'blok',
    'tyutchev'
  ]
  
  $scope.submitSeed = function() {
    if($scope.poetForm.$valid) {
      $http.post('/generate/' + $scope.poet, {
        'seed': $scope.seed
      }).then(function(response) {
        $scope.result = response.data;
      });
    }
  }
});