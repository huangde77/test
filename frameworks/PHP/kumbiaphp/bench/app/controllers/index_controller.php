<?php

/**
 * Controller por defecto si no se usa el routes
 *
 */
class IndexController extends AppController
{

    public function index()
    {
        View::select(null, null);
        header('Content-Type: text/plain');
        echo 'Hello, World!';
    }
}
