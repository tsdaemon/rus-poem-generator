'use strict';

angular.module('poetry', ['diff'])
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
  ];
  
  $scope.submitSeed = function() {
    if($scope.poetForm.$valid) {
      var data = {
        'seed': $scope.seed
      };
      if($scope.random) {
        data['random'] = $scope.random;
      }
      $http.post('/generate/' + $scope.poet, data).then(function(response) {
        $scope.result = response.data;
      });
    }
  }
});