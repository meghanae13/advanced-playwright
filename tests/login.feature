Feature: Login functionality

  Background:
    Given the login page is open

  Scenario: Successful login
    When the user enters valid credentials
    And the user clicks the login button
    Then the dashboard should be displayed

  Scenario: Invalid login
    When the user enters invalid credentials
    And the user clicks the login button
    Then an error message should be displayed