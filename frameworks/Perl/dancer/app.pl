#!/usr/bin/env perl
use strict;
use warnings;

use Dancer ':syntax';
use DBI;
use JSON::XS;  # Ensure that the fast implementation of the serializer is installed

set serializer => 'JSON';

my $dsn = "dbi:mysql:database=hello_world;host=127.0.0.1;port=3306";
my $dbh = DBI->connect( $dsn, 'benchmarkdbuser', 'benchmarkdbpass', {} );
my $sth = $dbh->prepare("SELECT * FROM World where id = ?");

get '/json' => sub {
    { message => 'Hello, World!' }
};

get '/db' => sub {
    my $queries = params->{queries} || 1;
    if ( $queries + 0 != $queries) {
        $queries = 1;
    }
    my @response;
    for ( 1 .. $queries ) {
        my $id = int rand 10000 + 1;
        $sth->execute($id);
        if ( my $row = $sth->fetchrow_hashref ) {
            if ( $queries == 1 ) {
                return { id => $id, randomNumber => $row->{randomNumber} };
            }
            else {
                push @response,
                  { id => $id, randomNumber => $row->{randomNumber} };
            }
        }
    }
    return \@response;
};

Dancer->dance;
