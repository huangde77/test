<?php

declare(strict_types=1);
/**
 * This file is part of Hyperf.
 *
 * @link     https://www.hyperf.io
 * @document https://doc.hyperf.io
 * @contact  group@hyperf.io
 * @license  https://github.com/hyperf-cloud/hyperf/blob/master/LICENSE
 */

namespace App\Controller;

use App\Model\Fortune;
use App\Model\World;
use App\Render;
use Hyperf\Di\Annotation\Inject;
use Hyperf\HttpServer\Annotation\Controller;
use Hyperf\HttpServer\Annotation\GetMapping;
use Hyperf\HttpServer\Contract\ResponseInterface;
use Hyperf\Utils\Coroutine\Concurrent;

/**
 * @Controller
 */
class IndexController
{

    /**
     * @Inject()
     * @var Render
     */
    private $render;

    /**
     * @Inject()
     * @var ResponseInterface
     */
    private $response;

    /**
     * @GetMapping(path="/json")
     */
    public function json()
    {
        return $this->response->json(['message' => 'Hello, World!']);
    }

    /**
     * @GetMapping(path="/db")
     */
    public function db()
    {
        return $this->response->json(World::find(random_int(1, 10000)));
    }

    /**
     * @GetMapping(path="/queries/[{queries}]")
     */
    public function queries($queries = 1)
    {
        $queries = $this->clamp($queries);

        $concurrent = new Concurrent(20);
        $rows = [];

        while ($queries--) {
            $concurrent->create(function () use (&$rows) {
                $rows[] = World::find(random_int(1, 10000));
            });
        }

        return $this->response->json($rows);
    }

    /**
     * @GetMapping(path="/fortunes")
     */
    public function fortunes()
    {
        $rows = Fortune::all();

        $insert = new Fortune();
        $insert->id = 0;
        $insert->message = 'Additional fortune added at request time.';

        $rows->add($insert);
        $rows = $rows->sortBy('message');

        return $this->render->render('fortunes', ['rows' => $rows]);
    }

    /**
     * @GetMapping(path="/updates/[{queries}]")
     */
    public function updates($queries = 1)
    {
        $queries = $this->clamp($queries);

        $concurrent = new Concurrent(20);
        $rows = [];

        while ($queries--) {
            $concurrent->create(function () use (&$rows) {
                $row = World::find(random_int(1, 10000));
                $row->randomNumber = random_int(1, 10000);
                $row->save();
                $rows[] = $row;
            });
        }

        return $this->response->json($rows);
    }

    /**
     * @GetMapping(path="/plaintext")
     */
    public function plaintext()
    {
        return $this->response->raw('Hello, World!');
    }

    private function clamp($value): int
    {
        if (! is_numeric($value) || $value < 1) {
            return 1;
        }
        if ($value > 500) {
            return 500;
        }
        return (int)$value;
    }
}
