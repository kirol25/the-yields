-- Runs once when the postgres container is first initialised.
-- Creates a separate database for the test suite so test runs
-- never touch the main development database.
CREATE DATABASE the_yields_test;
